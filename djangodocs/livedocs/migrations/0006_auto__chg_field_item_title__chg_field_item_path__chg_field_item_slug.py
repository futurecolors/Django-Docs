# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Item.title'
        db.alter_column('livedocs_item', 'title', self.gf('django.db.models.fields.CharField')(max_length=999))

        # Changing field 'Item.path'
        db.alter_column('livedocs_item', 'path', self.gf('django.db.models.fields.CharField')(max_length=999))

        # Changing field 'Item.slug'
        db.alter_column('livedocs_item', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=999))


    def backwards(self, orm):
        
        # Changing field 'Item.title'
        db.alter_column('livedocs_item', 'title', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'Item.path'
        db.alter_column('livedocs_item', 'path', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'Item.slug'
        db.alter_column('livedocs_item', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=100))


    models = {
        'livedocs.item': {
            'Meta': {'object_name': 'Item'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['livedocs.Item']"}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '1000', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['livedocs.Version']"})
        },
        'livedocs.version': {
            'Meta': {'object_name': 'Version'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['livedocs']