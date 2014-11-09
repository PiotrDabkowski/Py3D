import ctypes
import threading
import time

class timeout:
    def __init__(self, timeout, kill_on_timeout=True):
        self.__timeout = timeout
        self.__kill_on_timeout = kill_on_timeout

    def __call__(self, func):
        def prep_func(*args, **kwargs):
            result = args[0]
            args = tuple(list(args)[1:])
            try:
                result.append(func(*args, **kwargs))
            except Exception as e:
                result.append(e)
                
        def timeout_func(*args, **kwargs):
            result = []
            args = tuple([result]+list(args))
            t = threading.Thread(target=prep_func, args=args, kwargs=kwargs)
            t.daemon = True
            t.start()
            timeout_time = self.__timeout+time.time()
            while True:
              try:
                if time.time()>=timeout_time:
                    if self.__kill_on_timeout:
                        try:
                            terminate_thread(t)
                        except:
                            raise TimeoutReached('Could not kill the thread!')
                    raise TimeoutReached('Timeout reached! Thread killed.')
                if result:
                    if not issubclass(type(result[0]), BaseException):
                        return result[0] 
                    raise result[0]
                time.sleep(0.001)
              except KeyboardInterrupt:
                  try:
                      terminate_thread(t)
                  except:
                      print 'Could not kill the thread!'
                  raise KeyboardInterrupt('')
        return timeout_func

            
def terminate_thread(thread):
    if not thread.isAlive():
        return None
    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError('err')
    elif res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError('err')

class TimeoutReached(Exception):
    pass

@timeout(0.4)
def f(s=2):
    time.sleep(s)
    return s
