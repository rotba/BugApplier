import filecmp
import os
import unittest
import Applier
from mvnpy import Repo as MavenRepo
from mvnpy import mvn
import shutil


test_dir  = os.path.join(os.getcwd(), 'test_files')
TIKA_DB_DIR = os.path.join(Applier.DATABASE,'tika')
TIKA_56_DATA_DIR = os.path.join(os.getcwd(),'datas\\TIKA_56\\tika')
TIKA_56_GEN_DATA_DIR = os.path.join(os.getcwd(),'datas\\TIKA_56_GEN\\tika')

class TestApplier(unittest.TestCase):

    def setUp(self):
        pass
        if os.path.isdir(TIKA_DB_DIR):
            shutil.rmtree(TIKA_DB_DIR, ignore_errors=True)

    def tearDown(self):
        pass

    def test_init(self):
        shutil.copytree(TIKA_56_DATA_DIR, TIKA_DB_DIR)
        expected_requested_path = os.path.join(test_dir, 'test_init')
        expected_repo_path = os.path.join(expected_requested_path, 'tika')
        applier = Applier.Applier('https://github.com/apache/tika', expected_requested_path)
        self.assertTrue(os.path.isdir(expected_repo_path))

    def test_apply_tika_56(self):
        testcase_dir = os.path.join(test_dir, 'test_apply_tika_56')
        if not os.path.isdir(os.path.join(test_dir, 'test_apply_tika_56')):
            os.mkdir(testcase_dir)
        shutil.copytree(TIKA_56_DATA_DIR, TIKA_DB_DIR)
        applier = Applier.Applier('https://github.com/apache/tika', testcase_dir)
        mvn_repo = MavenRepo.Repo(applier.proj_dir)
        testcase_id_suffix = 'tika\\src\\test\\java\\org\\apache\\tika\\mime\\TestMimeTypes.java#TestMimeTypes#None_testCaseSensitivity()'
        bugs = applier.get_bugs('TIKA-56', 'b12c01d9b56053554cec501aab0530f7f4352daf')
        bug = [b for b in bugs if b.bugged_testcase.id.endswith(testcase_id_suffix)][0]
        applier.apply(bug)
        os.system('mvn test -f '+applier.proj_dir+' -fn')
        testclasses = mvn_repo.get_tests(applier.proj_dir)
        testcases = mvn.get_testcases(testclasses)
        testcase = [t for t in testcases if t.id.endswith('TestMimeTypes#None_testCaseSensitivity()')][0]
        testcase.parent.look_for_report()
        self.assertTrue(testcase.failed)

    def test_apply_generated_test_tika_56(self):
        testcase_dir = os.path.join(test_dir, 'test_apply_generated_test_tika_56')
        if not os.path.isdir(os.path.join(test_dir, 'test_apply_generated_test_tika_56')):
            os.mkdir(testcase_dir)
        shutil.copytree(TIKA_56_GEN_DATA_DIR, TIKA_DB_DIR)
        applier = Applier.Applier('https://github.com/apache/tika', testcase_dir)
        mvn_repo = MavenRepo.Repo(applier.proj_dir)
        testcase_id_infix = 'tika\\src\\test\\java\\org\\apache\\tika\\mime\\MimeTypes_ESTest.java'
        bugs = applier.get_bugs('TIKA-56', 'b12c01d9b56053554cec501aab0530f7f4352daf')
        valid_bugs = filter(lambda b: b.valid,bugs)
        bug = valid_bugs[0]
        applier.apply(bug)
        os.system('mvn test -f '+applier.proj_dir+' -fn')
        testclasses = mvn_repo.get_tests(applier.proj_dir)
        testcases = mvn.get_testcases(testclasses)
        testcases = [t for t in testcases if t in map(lambda x: x.bugged_testcase, valid_bugs)]
        for testcase in testcases:
            testcase.parent.look_for_report()
            self.assertTrue(testcase.failed)



if __name__ == '__main__':
    unittest.main()
