from odoo import models, fields


class LibraryBookCategory(models.Model):
    _name = 'library.book.category'
    _description = 'Book Category'

    name = fields.Char(string='Category Name', required=True, translate=True)
    parent_id = fields.Many2one('library.book.category', string='Parent Category')
    child_ids = fields.One2many('library.book.category', 'parent_id', string='Subcategories')
    book_ids = fields.One2many('library.book', 'category_id', string='Books in this Category')