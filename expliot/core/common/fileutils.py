#
#
# expliot - Internet Of Things Exploitation Framework
# 
# Copyright (C) 2018  Aseem Jakhar
#
# Email:   aseemjakhar@gmail.com
# Twitter: @aseemjakhar
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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


# Common file utility methods that can be used across the framework


def readlines(file):
    """
    Helper method for reading one line at a time from a file and yielding it for loops.
    The file is closed automatically even if the caller exits the loop early (break, exception
    etc) Thanks to with statement :)

    :param file: The file to read data from.
    :return: yield a line in a loop
    """
    with open(file) as f:
        for line in f:
            yield line.rstrip()


def readlines_both(file1, file2):
    """
    Helper method for reading one line at a time from two files and yielding them for loops.
    For each line in file1 it will also loop through all lines of file2. Total no. of yields is
    lines in file1 x lines in file2
    The files are closed automatically even if the caller exits the loop early (break, exception
    etc) Thanks to with statement :)

    :param file1: The first file to read data from
    :param file2: The second file to read data from
    :return:
    """
    with open(file1) as f1:
        for l1 in f1:
            with open(file2) as f2:
                for l2 in f2:
                    yield l1.rstrip(), l2.rstrip()
