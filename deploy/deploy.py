import glob
import fnmatch
import shutil

APP_FOLDER = '/tmp/app'

def is_excluded(file, exclusions):
    for exclusion in exclusions:
        print(file, exclusion)
        if fnmatch.fnmatch(file, exclusion):
            return True
    return False

def copy(src, dst, options):
    print(f"{src} -> {dst} ({options})")
    if '*' in src:
        exclusions = options.get('exclude', "")
        exclusions = exclusions.split(',')
        files = glob.glob(src)
        for file in files:
            if not is_excluded(file, exclusions):
                print(f"- {file} {dst}")
                # shutil.copy(file, dst)

def parse(line):
    src, dest, *options = line.rstrip().split(' ')
    # fixme replace dest with the temp path
    dest = dest.replace("$APP", APP_FOLDER)
    options = "".join(options).strip('()').split(";")
    optkw = {}
    if options:
        for option in options:
            if ':' in option:
                key, value = option.split(":")
                optkw[key] = value
    return src, dest, optkw

# shutil.rmtree(APP_FOLDER)
with open('deploy/deploy.txt') as fd:
    for line in fd:
        source, dest, options = parse(line)
        copy(source, dest, options)
