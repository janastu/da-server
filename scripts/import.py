import os
import pymongo
import gridfs
import click


@click.command()
@click.option('--database', prompt='Database name in which files' +
              'will be stored', help='test_name')
@click.option('--directory', prompt='Directory to look for files',
              help='/vol/foo/bar')
@click.pass_context
def import_directory(ctx, database, directory):
    ctx.obj['gfs'] = gridfs.GridFS(pymongo.MongoClient()[database])
    os.path.walk(directory, add_files, ctx)


def add_files(arg, dirname, filenames):
    gfs = arg.obj['gfs']
    for f in filenames:
        if os.path.isfile(os.path.join(dirname, f)):
            with open(os.path.join(dirname, f), 'r') as fd:
                print "adding file, ", os.path.join(dirname, f)
                gfs.put(fd.read(), **{'filename': f})

if __name__ == "__main__":
    import_directory(obj={})
