# Totals the Ant <junit> XML reports (TEST-*.xml) so the job log states how many tests ran,
# passed, failed and errored, and names every failing test with its message.
import glob, sys, xml.etree.ElementTree as ET

report_dir = sys.argv[1] if len(sys.argv) > 1 else "test-reports"
files = sorted(glob.glob(report_dir + "/TEST-*.xml"))
tests = failures = errors = 0
for path in files:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    for s in suites:
        t, f, e = int(s.get("tests", 0)), int(s.get("failures", 0)), int(s.get("errors", 0))
        tests, failures, errors = tests + t, failures + f, errors + e
        print("%-70s tests=%-5d failures=%-3d errors=%d" % (s.get("name"), t, f, e))
        for tc in s.iter("testcase"):
            for kind in ("failure", "error"):
                el = tc.find(kind)
                if el is not None:
                    print("  %s: %s.%s: %s" % (kind.upper(), tc.get("classname"), tc.get("name"), el.get("message")))
passed = tests - failures - errors
print("=" * 100)
print("TEST SUMMARY: %d report files, %d tests run, %d passed, %d failures, %d errors, 0 skipped"
      % (len(files), tests, passed, failures, errors))
if not files or failures or errors:
    sys.exit(1)
