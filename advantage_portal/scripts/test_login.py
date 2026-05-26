import urllib.request
import urllib.parse
import http.cookiejar
import socket
from datetime import datetime


def main():
    start = datetime.utcnow()
    print(f"[test_login] START: {start.isoformat()}Z")

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    url = 'http://127.0.0.1:5000/login'
    creds = [
        ('2000000001','admin@2025','admin'),
        ('coordinator','admin123','coordinator'),
        ('1234567890','student123','student1'),
        ('student2025','Student@2025','student2025')
    ]
    results = []

    for uname, pwd, label in creds:
        data = urllib.parse.urlencode({'username': uname, 'password': pwd}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        print(f"[test_login] Hitting URL: {url} for user={uname}")
        try:
            # fail fast if server is not accepting connections
            with opener.open(req, timeout=5) as resp:
                final = resp.geturl()
                body = resp.read().decode('utf-8', errors='ignore')
                # determine success: redirect to admin_dashboard or student_home
                if final.endswith('/admin_dashboard') or final.endswith('/dashboard') or '/student/home' in final:
                    results.append((label, True, final, ''))
                else:
                    # check for Arabic error text
                    if 'بيانات غير صحيحة' in body:
                        results.append((label, False, final, 'بيانات غير صحيحة'))
                    else:
                        results.append((label, False, final, 'unknown failure'))
        except urllib.error.URLError as e:
            # connection refused, timeout, DNS failure, etc.
            err = str(e)
            print(f"[test_login] Connection error for user={uname}: {err}")
            results.append((label, False, '', f"connection error: {err}"))
        except socket.timeout as e:
            print(f"[test_login] Timeout for user={uname}")
            results.append((label, False, '', 'timeout'))
        except Exception as e:
            print(f"[test_login] Unexpected error for user={uname}: {e}")
            results.append((label, False, '', str(e)))

    for r in results:
        print(r)

    end = datetime.utcnow()
    print(f"[test_login] END: {end.isoformat()}Z (duration: {end - start})")


if __name__ == '__main__':
    main()
