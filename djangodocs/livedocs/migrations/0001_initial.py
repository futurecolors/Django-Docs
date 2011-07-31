# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Version'
        db.create_table('livedocs_version', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('is_default', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('livedocs', ['Version'])

        # Adding model 'Item'
        db.create_table('livedocs_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=1000, db_index=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['livedocs.Item'])),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['livedocs.Version'])),
            ('is_root', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('livedocs', ['Item'])

        # Adding model 'ItemAnchor'
        db.create_table('livedocs_itemanchor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['livedocs.Item'])),
        ))
        db.send_create_signal('livedocs', ['ItemAnchor'])


    def backwards(self, orm):
        
        # Deleting model 'Version'
        db.delete_table('livedocs_version')

        # Deleting model 'Item'
        db.delete_table('livedocs_item')

        # Deleting model 'ItemAnchor'
        db.delete_table('livedocs_itemanchor')


    models = {
        'livedocs.item': {
            'Meta': {'object_name': 'Item'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_root': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        'livedocs.itemanchor': {
            'Meta': {'object_name': 'ItemAnchor'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['livedocs.Item']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        'livedocs.version': {
            'Meta': {'object_name': 'Version'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['livedocs']
