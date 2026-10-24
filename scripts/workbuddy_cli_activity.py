"""WB CLI lifecycle metadata and read-only activity discovery; no model requests."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def status_directory():
    return Path(os.environ.get('LOCALAPPDATA', Path.home()/'.local'/'state'))/'CodexDispatcher'/'workbuddy-cli'


def process_birth(pid):
    try:
        if os.name == 'nt':
            from ctypes import wintypes
            kernel=ctypes.WinDLL('kernel32',use_last_error=True)
            kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
            kernel.OpenProcess.restype=wintypes.HANDLE
            kernel.GetProcessTimes.argtypes=[wintypes.HANDLE]+[ctypes.POINTER(wintypes.FILETIME)]*4
            kernel.CloseHandle.argtypes=[wintypes.HANDLE]
            handle=kernel.OpenProcess(0x1000,False,int(pid))
            if not handle:return None
            try:
                times=[wintypes.FILETIME() for _ in range(4)]
                if not kernel.GetProcessTimes(handle,*(ctypes.byref(v) for v in times)):return None
                return str((times[0].dwHighDateTime<<32)|times[0].dwLowDateTime)
            finally:kernel.CloseHandle(handle)
        return Path(f'/proc/{int(pid)}/stat').read_text().rsplit(')',1)[1].split()[19]
    except (OSError,ValueError,IndexError):return None


def read_active(root=None):
    root=Path(root) if root else status_directory()
    rows=[]
    try:files=list(root.glob('*.json'))[:256]
    except OSError:return rows
    for file in files:
        try:
            if file.is_symlink() or file.stat().st_size>16384:continue
            item=json.loads(file.read_text(encoding='utf-8'))
            key=item.get('key','')
            if item.get('schema')!=1 or len(key)!=64 or any(c not in '0123456789abcdef' for c in key) or key!=file.stem:continue
            if type(item.get('startedAt')) is not int or item['startedAt']<0:continue
            pid=item.get('runnerPid')
            if type(pid) is not int or pid<=0 or not item.get('runnerBirth') or process_birth(pid)!=item['runnerBirth']:continue
            job=Path(item['jobDir'])
            if not job.is_absolute() or not job.is_dir():continue
            # Do not accept arbitrary executable/document targets from metadata.
            stdout=job/'workbuddy-cli.stdout.log';stderr=job/'workbuddy-cli.stderr.log'
            if not stdout.is_file() or stdout.is_symlink() or stderr.is_symlink():continue
            log=stderr if stdout.stat().st_size==0 and stderr.is_file() and stderr.stat().st_size>0 else stdout
            rows.append({'key':key,'title':str(item.get('title') or '分工任务')[:96],
                         'model':str(item.get('model') or '')[:80],'startedAt':item['startedAt'],
                         'runnerPid':pid,'runnerBirth':item['runnerBirth'],
                         'jobDir':str(job.resolve()),'logFile':str(log.resolve())})
        except (OSError,ValueError,KeyError,TypeError):continue
    return sorted(rows,key=lambda r:r['startedAt'],reverse=True)


def run_workbuddy(command,*,timeout,cwd,env,job_id,title,model,status_root=None):
    cwd=Path(cwd).resolve()
    stdout_file=cwd/'workbuddy-cli.stdout.log';stderr_file=cwd/'workbuddy-cli.stderr.log'
    root=Path(status_root) if status_root is not None else status_directory()
    key=hashlib.sha256(f'{cwd}|{os.getpid()}|{job_id}'.encode('utf-8')).hexdigest()
    target=root/(key+'.json');temporary=root/(key+'.tmp')
    birth=process_birth(os.getpid())
    published=False
    # Opening the logs before publishing ensures every visible card has a real target.
    with stdout_file.open('wb') as out,stderr_file.open('wb') as err:
        try:
            if birth:
                root.mkdir(parents=True,exist_ok=True)
                item={'schema':1,'key':key,'jobId':str(job_id)[:160],
                      'title':' '.join(str(title).split())[:96] or '分工任务',
                      'model':str(model or '')[:80],'jobDir':str(cwd),
                      'runnerPid':os.getpid(),'runnerBirth':birth,'startedAt':int(time.time()*1000)}
                temporary.write_text(json.dumps(item,ensure_ascii=False),encoding='utf-8')
                os.replace(temporary,target);published=True
        except OSError:
            pass  # Monitoring must not prevent the original dispatch.
        try:
            completed=subprocess.run(command,stdout=out,stderr=err,timeout=timeout,
                                     check=False,cwd=cwd,env=env)
        except subprocess.TimeoutExpired as error:
            error.stdout=stdout_file.read_text(encoding='utf-8',errors='replace')
            error.stderr=stderr_file.read_text(encoding='utf-8',errors='replace')
            raise
        finally:
            if published:
                try:target.unlink(missing_ok=True)
                except OSError:pass
    return subprocess.CompletedProcess(command,completed.returncode,
        stdout_file.read_text(encoding='utf-8',errors='replace'),
        stderr_file.read_text(encoding='utf-8',errors='replace'))


if __name__=='__main__':
    print(json.dumps({'rows':read_active(sys.argv[1] if len(sys.argv)>1 else None)},ensure_ascii=True))
