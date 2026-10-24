import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'workbuddy_cli_activity.py'
if MODULE.exists():
    spec = importlib.util.spec_from_file_location('wb_activity', MODULE)
    activity = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(activity)
else:
    activity = None


class ActivityTests(unittest.TestCase):
    def test_corrupt_record_does_not_hide_a_valid_live_task(self):
        self.assertIsNotNone(activity, 'WB CLI lifecycle publisher is missing')
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);job=root/'job';job.mkdir();live=root/'live';live.mkdir()
            (job/'workbuddy-cli.stdout.log').write_text('ok')
            row={'schema':1,'key':'a'*64,'title':'test','startedAt':1,'jobDir':str(job),
                 'runnerPid':os.getpid(),'runnerBirth':activity.process_birth(os.getpid())}
            (live/(row['key']+'.json')).write_text(json.dumps(row),encoding='utf-8')
            broken={**row,'key':'b'*64,'startedAt':'corrupt'}
            (live/(broken['key']+'.json')).write_text(json.dumps(broken),encoding='utf-8')
            self.assertEqual([r['key'] for r in activity.read_active(live)],['a'*64])

    def test_reader_rejects_dead_or_reused_process_and_foreign_log_target(self):
        self.assertIsNotNone(activity, 'WB CLI lifecycle publisher is missing')
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);job=root/'job';job.mkdir();live=root/'live';live.mkdir()
            (job/'workbuddy-cli.stdout.log').write_text('ok')
            key='a'*64
            row={'schema':1,'key':key,'title':'test','startedAt':1,'jobDir':str(job),
                 'runnerPid':os.getpid(),'runnerBirth':activity.process_birth(os.getpid())}
            path=live/(key+'.json')
            path.write_text(json.dumps(row),encoding='utf-8')
            self.assertEqual(len(activity.read_active(live)),1)
            row['runnerBirth']='reused';path.write_text(json.dumps(row),encoding='utf-8')
            self.assertEqual(activity.read_active(live),[])
            row['runnerPid']=2147483647;path.write_text(json.dumps(row),encoding='utf-8')
            self.assertEqual(activity.read_active(live),[])
            row['runnerPid']=os.getpid();row['runnerBirth']=activity.process_birth(os.getpid())
            path.write_text(json.dumps(row),encoding='utf-8')
            (job/'workbuddy-cli.stdout.log').unlink()
            self.assertEqual(activity.read_active(live),[])

    def test_running_metadata_and_live_log_then_cleanup(self):
        self.assertIsNotNone(activity, 'WB CLI lifecycle publisher is missing')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            job = root / 'job'; job.mkdir()
            status_root = root / 'live'
            results = []
            worker = threading.Thread(target=lambda: results.append(activity.run_workbuddy(
                [sys.executable, '-u', '-c', "import time;print('LIVE_UTF8_OK',flush=True);time.sleep(.8)"],
                timeout=4, cwd=job, env=os.environ.copy(), job_id='task1', title='测试任务',
                model='test', status_root=status_root)))
            worker.start()
            deadline = time.monotonic() + 3
            records = []
            while time.monotonic() < deadline:
                records = list(status_root.glob('*.json'))
                if records and (job/'workbuddy-cli.stdout.log').exists() and 'LIVE_UTF8_OK' in (job/'workbuddy-cli.stdout.log').read_text():
                    break
                time.sleep(.02)
            self.assertEqual(len(records), 1)
            row = json.loads(records[0].read_text(encoding='utf-8'))
            self.assertEqual(row['title'], '测试任务')
            self.assertNotIn('prompt', row)
            self.assertEqual(row['runnerBirth'], activity.process_birth(os.getpid()))
            self.assertIn('LIVE_UTF8_OK', (job/'workbuddy-cli.stdout.log').read_text())
            worker.join(5)
            self.assertEqual(results[0].returncode, 0)
            self.assertIn('LIVE_UTF8_OK', results[0].stdout)
            self.assertEqual(list(status_root.glob('*.json')), [])

    def test_timeout_keeps_output_and_removes_active_record(self):
        self.assertIsNotNone(activity, 'WB CLI lifecycle publisher is missing')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(subprocess.TimeoutExpired) as caught:
                activity.run_workbuddy([sys.executable,'-u','-c',"import time;print('before timeout',flush=True);time.sleep(5)"],
                    timeout=.3,cwd=root,env=os.environ.copy(),job_id='timeout',title='test',model='',status_root=root/'live')
            self.assertIn('before timeout', caught.exception.stdout)
            self.assertEqual(list((root/'live').glob('*.json')), [])

    def test_unwritable_monitor_does_not_block_the_cli(self):
        self.assertIsNotNone(activity, 'WB CLI lifecycle publisher is missing')
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); blocked=root/'not-a-directory';blocked.write_text('file')
            result=activity.run_workbuddy([sys.executable,'-c',"print('OK')"],timeout=3,cwd=root,
                env=os.environ.copy(),job_id='fallback',title='test',model='',status_root=blocked)
            self.assertEqual(result.returncode,0)

if __name__ == '__main__':
    unittest.main()
