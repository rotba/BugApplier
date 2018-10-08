import filecmp
import os
import unittest
import Applier
from mvnpy import Repo as MavenRepo
from mvnpy import mvn
import shutil


test_dir  = os.path.join(os.getcwd(), 'test_files')

class TestApplier(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        expected_requested_path = os.path.join(test_dir, 'test_init')
        expected_repo_path = os.path.join(expected_requested_path, 'tika')
        expected_data_path = os.path.join(expected_requested_path, 'data')
        applier = Applier.Applier('https://github.com/apache/tika', expected_requested_path, 'TIKA-56')
        self.assertTrue(os.path.isdir(expected_repo_path))
        self.assertTrue(os.path.isdir(expected_data_path))

    def test_apply(self):
        applier = Applier.Applier('https://github.com/apache/tika', os.path.join(test_dir, 'test_apply'))
        mvn_repo = MavenRepo.Repo(applier.proj_dir)
        testcase_id = 'C:\\Users\\user\\Code\\Python\\BugMiner\\tested_project\\tika\\src\\test\\java\\org\\apache\\tika\\mime\\TestMimeTypes.java#TestMimeTypes#None_testCaseSensitivity()'
        bugs = applier.get_bugs('TIKA-56', 'b12c01d9b56053554cec501aab0530f7f4352daf')
        bug = [b for b in bugs if b.bugged_testcase.id == testcase_id ][0]
        applier.apply(bug)
        os.system('mvn test -f '+applier.proj_dir+' -fn')
        testclasses = mvn_repo.get_tests(applier.proj_dir)
        testcases = mvn.get_testcases(testclasses)
        testcase = [t for t in testcases if t.id.endswith('TestMimeTypes#None_testCaseSensitivity()')][0]
        testcase.parent.look_for_report()
        self.assertTrue(testcase.failed)



if __name__ == '__main__':
    unittest.main()
