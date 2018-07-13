#
#
# expliot - Internet Of Things Security Testing and Exploitation Framework
# 
# Copyright (C) 2018  Aseem Jakhar
#
# Email:   aseemjakhar@gmail.com
# Twitter: @aseemjakhar
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#


import inspect
import pkgutil
import importlib


import sys
sys.path.append("..")

from expliot.core.tests.test import Test

class TestSuite(dict):
    """
    TestSuite class inherites from dict and stores all the test cases
    from plugins package name specified in __init__()
    """

    testcls = [Test]

    def __init__(self, pkgname='expliot.plugins'):
        """
        Initialize the test suite with the plugins in the package
        :param pkgname: The package to load test case plugins from or 'expliot.plugins' if None specified
        """
        #self.tmap = {}
        self.import_plugins(pkgname)

    def import_plugins(self, pkgname):
        """
        Imports all tests from the specified Package into a dict
        :param pkgname: The packageto load all test case plugins from
        :return: void
        """
        pkgs = [pkgname]
        # Import from all subpackages recursively
        while len(pkgs) > 0:
            pkg = pkgs.pop()
            pmod = importlib.import_module(pkg)
            prefix =  pmod.__name__ + "."
            for finder, name, ispkg in pkgutil.iter_modules(pmod.__path__, prefix):
                if ispkg:
                    pkgs.append(name)
                else:
                    mod = importlib.import_module(name)
                    for tname, klass in inspect.getmembers(mod):
                        if inspect.isclass(klass) and issubclass(klass, Test) and klass not in TestSuite.testcls:
                            self[tname.lower()] = klass


#if __name__ == "__main__":
#    ts = TestSuite()
#    t = ts.get('ssample', None)
#    print(t)
