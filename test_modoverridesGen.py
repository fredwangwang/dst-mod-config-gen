import unittest

import modoverridesGen


class ModOverridesGenTests(unittest.TestCase):
    def test_ModInfoConfig_merge_bool(self):
        this_config = modoverridesGen.ModInfoConfig(label="label1", default=False)
        other_config = modoverridesGen.ModInfoConfig(name="name1", label="label1", default=True)

        self.assertEqual(this_config.merge(other_config),
                         modoverridesGen.ModInfoConfig(name="name1", label="label1", default=False))

    def test_ModInfoConfig_merge_none(self):
        this_config = modoverridesGen.ModInfoConfig(label="label1", default=None)
        other_config = modoverridesGen.ModInfoConfig(name="name1", label="label1", default=False)

        self.assertEqual(this_config.merge(other_config),
                         modoverridesGen.ModInfoConfig(name="name1", label="label1", default=False))

    def test_ModInfoConfig_merge_other(self):
        this_config = modoverridesGen.ModInfoConfig(label="label1", default="123")
        other_config = modoverridesGen.ModInfoConfig(name="name1", label="label1", default=True)

        self.assertEqual(this_config.merge(other_config),
                         modoverridesGen.ModInfoConfig(name="name1", label="label1", default="123"))


if __name__ == '__main__':
    unittest.main()
