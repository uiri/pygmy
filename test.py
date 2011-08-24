import browser, sys

url = sys.stdin.readline()
web = browser.Browser(url.rstrip())
web.main()
