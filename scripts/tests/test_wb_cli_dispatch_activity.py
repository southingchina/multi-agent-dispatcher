"""Real dispatcher subprocess + local fake node. No model/network requests."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

DISPATCH=Path(__file__).resolve().parents[1]/'dispatch_cli.py'

class DispatchActivityTest(unittest.TestCase):
    def test_dispatch_publishes_live_task_and_preserves_normal_result(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);job=root/'job';local=root/'local'
            fake=root/'fake_wb.py'
            fake.write_text("import json,time\nprint(json.dumps([{'type':'result','result':'WB_CLI_OBSERVER_TEST_OK'}]),flush=True)\ntime.sleep(1)\n",encoding='utf-8')
            registry=root/'registry.json'
            registry.write_text(json.dumps({'agents':[{'id':'workbuddy-cli','family':'workbuddy','surface':'cli',
                'enabled':True,'command':[sys.executable,'-u',str(fake)],'args':[],
                'reported_model':'local-test','response_parser':'codebuddy-log'}]}),encoding='utf-8')
            env=os.environ.copy();env['LOCALAPPDATA']=str(local);env['PYTHONIOENCODING']='utf-8'
            process=subprocess.Popen([sys.executable,str(DISPATCH),'--agent','workbuddy-cli','--registry',str(registry),
                '--job-dir',str(job),'--prompt','No real model call','--task-title','WB CLI 接入测试'],
                stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            try:
                deadline=time.monotonic()+4;records=[]
                while time.monotonic()<deadline:
                    records=list((local/'CodexDispatcher'/'workbuddy-cli').glob('*.json'))
                    if records:break
                    time.sleep(.02)
                self.assertEqual(len(records),1)
                row=json.loads(records[0].read_text(encoding='utf-8'))
                self.assertEqual(row['title'],'WB CLI 接入测试')
                self.assertNotIn('prompt',row)
                out,err=process.communicate(timeout=8)
                self.assertEqual(process.returncode,0,err.decode('utf-8'))
                result=json.loads(out)
                self.assertEqual(result['status'],'completed')
                self.assertEqual(result['response'],'WB_CLI_OBSERVER_TEST_OK')
                self.assertEqual(list((local/'CodexDispatcher'/'workbuddy-cli').glob('*.json')),[])
                self.assertTrue((job/'workbuddy-cli.stdout.log').is_file())
            finally:
                if process.poll() is None:process.kill();process.communicate()

if __name__=='__main__':unittest.main()
