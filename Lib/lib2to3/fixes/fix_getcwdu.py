"""
Fixer that changes os.getcwdu() to os.getcwd().
"""
# Author: Victor Stinner

# Local imports
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name

kundi FixGetcwdu(fixer_base.BaseFix):
    BM_compatible = Kweli

    PATTERN = """
              power< 'os' trailer< dot='.' name='getcwdu' > any* >
              """

    eleza transform(self, node, results):
        name = results["name"]
        name.replace(Name("getcwd", prefix=name.prefix))
