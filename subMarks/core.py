from flask import request, session, g, redirect, url_for, abort, render_template, flash, jsonify, Response, make_response

import urllib2

from instruments.core import public_endpoint

from subMarks import blueprint
import database
                   

@blueprint.route('/')
def index():
    page = request.args.get('p')
    if not page:
        page = 0
    else: 
        page = int(page)
        
    bookmarks, more_bookmarks = database.get_recent_bookmarks(page)
    return render_template('subMarks.html',
                            bookmarks=bookmarks,
                            page=page,
                            more_bookmarks=more_bookmarks,
                            projects=database.get_projects())
                            
                            
@blueprint.route('/create_tables')
def create_tables():
    database.create_tables()
    return redirect("%s#%s" % (request.referrer, blueprint.name))
                            
                            
@blueprint.route('/<project>/')
def show_project(project):
    bookmarks, project_name = database.get_project_bookmarks(project)
    if not project_name:
        abort(404)
    return render_template('project.html',
                            bookmarks=bookmarks,
                            project_name=project_name,
                            page=0,
                            more_bookmarks=False,
                            projects=database.get_projects())

@blueprint.route('/bm/')
@public_endpoint
def bookmark():
    url = request.args.get('url')
    bookmark_title = request.args.get('t')
    project = request.args.get('p')
    if url:
        url = resolve_url(url)
        if not bookmark_title:
            bookmark_title = url
    
        if project:
            database.save_bookmark(url, bookmark_title, project)
        else:
            database.save_bookmark(url, bookmark_title)

    r = make_response(render_template('bm.js'))
    r.mimetype='text/javascript'
    
    return r
    
    
def resolve_url(url):
    try:
        req = urllib2.urlopen(url)
        url_resolved = req.geturl()
    except:
        return url
    if '?utm_source=' in url_resolved:
        url_resolved = url_resolved[0:url_resolved.rfind('?utm_source')]
        
    return url_resolved
    
    
@blueprint.route('/bm/save/', methods=['post'])
@public_endpoint
def edit_bookmark():
    title = request.form.get('title')
    url = request.form.get('url')
    bookmark_id = request.form.get('bookmark_id')
    
    if title and url and bookmark_id:
        database.update_bookmark(bookmark_id, title, url)
        
    return redirect(request.referrer)
    
    
@blueprint.route('/search/', methods=['get', 'post'])
def search():
    search_string = request.form.get('search')
    
    bookmarks = database.search_for_bookmarks(search_string)
    
    return render_template('project.html',
                            bookmarks=bookmarks,
                            project_name="search results: %s" % search_string,
                            page=0,
                            more_bookmarks=False,
                            projects=database.get_projects())
    
    
@blueprint.route('/move/<int:bookmark_id>/<int:project_id>/')
def move_bookmark(bookmark_id, project_id):
    database.move_bookmark(bookmark_id, project_id)
    return redirect(url_for('subMarks.show_project', project=project_id))
    
    
@blueprint.route('/delete/<int:bookmark_id>/')
def delete_bookmark(bookmark_id):
    database.delete_bookmark(bookmark_id)
    return redirect(request.referrer)
    
    
@blueprint.route('/create_project/', methods=['post'])
def create_project():
    project = request.form.get('project')
    if project:
        database.create_project(project)
    return redirect(url_for('subMarks.index'))