#
#    Bemade Inc.
#
#    Copyright (C) 2023-June Bemade Inc. (<https://www.bemade.org>).
#    Author: Marc Durepos (Contact : marc@bemade.org)
#
#    This program is under the terms of the GNU Lesser General Public License,
#    version 3.
#
#    For full license details, see https://www.gnu.org/licenses/lgpl-3.0.en.html.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
{
    "name": "Many2one Confirm Creation",
    "version": "18.0.1.0.0",
    "summary": "Pop up a confirmation dialog when creating via a Many2one field",
    "category": "Web",
    "author": "Bemade Inc.",
    "website": "http://www.bemade.org",
    "license": "LGPL-3",
    "depends": ["web",'purchase'],
    "data": [
         'views/custom_purchase_order_line.xml',
        ],
    "assets": {
        "web.assets_backend": [
            "confirm_many2one_create/static/src/js/many2one_field.esm.js",
        ],
    },
    "installable": True,
    "auto_install": False,
}
