import os
import shutil
import random
import sys
import json
import argparse
import collections
import collections.abc
import logging
def main():
    parser = argparse.ArgumentParser(description='Randomise the assets of a Minecraft resource pack.')
    parser.add_argument('-p', '--pack', default='pack', type=str, dest='pack', help='specifies a resource pack folder')
    parser.add_argument('-s', '--seed', default=random.randrange(sys.maxsize), type=int, dest='seed', help='specifies a random seed')
    parser.add_argument('--noanimations', action='store_false', dest='animations', help='disables animations, fixes some missing textures')
    parser.add_argument('--alttextures', action='store_true', dest='alttextures', help='alternative texture randomization, only swaps blocks with other blocks, items with items, etc. supports animated textures')
    parser.add_argument('--notextures', action='store_false', dest='textures', help='disables randomised textures')
    parser.add_argument('--noblockstates', action='store_false', dest='blockstates', help='disables randomised block states')
    parser.add_argument('--nosounds', action='store_false', dest='sounds', help='disables randomised sounds')
    parser.add_argument('--notexts', action='store_false', dest='texts', help='disables randomised text')
    parser.add_argument('--nofonts', action='store_false', dest='fonts', help='disables randomised fonts')
    parser.add_argument('--noshaders', action='store_false', dest='shaders', help='disables randomised shaders')
    parser.add_argument('--models', action='store_true', dest='models', help='EXPERIMENTAL: randomised block/item models')

    args = parser.parse_args()
    resourcepack = args.pack
    randomseed = args.seed
    randomisetextures = args.textures
    randomisemodels = args.models
    randomiseanimations = args.animations
    randomiseblockstates = args.blockstates
    randomisesounds = args.sounds
    randomisetext = args.texts
    randomisefont = args.fonts
    randomise_shaders = args.shaders
    alttextures = args.alttextures
    return run(randomseed, randomisemodels, randomiseblockstates, randomisesounds, randomisetext, randomisefont, randomise_shaders, alttextures)


def run(data_folder, seed, randomize_textures: bool, randomize_models: bool, randomize_blockstates: bool, randomize_sounds: bool, randomize_text: bool, randomize_font: bool, randomize_shaders: bool=True, alt_textures: bool = False):
    random.seed(seed)
    data_folder="pack"
    if data_folder == "shuffle":
        return "The input resource pack may not be named 'shuffle'."
    if os.path.exists(os.path.join('shuffle')):
        return "Please remove the 'shuffle' folder before running this program."
    
    def makepath(path):
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except:
                print('DEBUG: tried to create an existing folder')

    if not (randomize_textures or randomize_models or randomize_blockstates or randomize_sounds or randomize_text or randomize_font or randomize_shaders):
        return 'Successfully randomised nothing!'
    if not os.path.exists(data_folder):makepath(data_folder)
    if not os.path.exists(os.path.join(data_folder, 'assets')):
        return 'Unable to locate resource pack folder! Please ensure you have extracted one properly, you should have an "assets" folder in the "'+data_folder+'" folder.'

    images = {}
    randimages = {}
    itemmodels = []
    blockmodels = []
    blockstates = []
    sounds = []
    randsounds = []
    languages = []
    specialtexts = []
    shaders = {'vsh': [], 'fsh': [], 'json': []}
    totaltextures = 0

    def processimage(imagepath):
        #print(imagepath.replace('.png', '.mcmeta'))
        #if randomiseanimations or os.path.exists()
        if not alt_textures:
            f = open(imagepath, mode='rb')
            header = f.read(26)
            f.close()
            width = int.from_bytes(header[16:20],'big',signed=False)
            height = int.from_bytes(header[20:24],'big',signed=False)
            dictkey = f"{width}x{height}"
            if dictkey not in images:
                images[dictkey] = []
            images[dictkey].append(imagepath)
        else:
            texturetype = imagepath.split(os.path.sep)[4]
            if texturetype not in images:
                images[texturetype] = []
            images[texturetype].append(imagepath)

    #find the files to swap
    for dirpath, dirs, files in os.walk(os.path.join(data_folder,"assets")):
        for file in files:
            fullfilepath = os.path.join(dirpath,file)
            mcraft = os.path.join(data_folder,'assets','minecraft')

            if file.endswith('.png') and (randomize_font or randomize_textures):
                if dirpath == os.path.join(mcraft,'textures','font') and randomize_font:
                    processimage(fullfilepath)
                    totaltextures += 1
                if dirpath != os.path.join(mcraft,'textures','font') and randomize_textures:
                    processimage(fullfilepath)
                    totaltextures += 1
            elif dirpath == os.path.join(mcraft,'models','item') and randomize_models:
                itemmodels.append(fullfilepath)
            elif dirpath == os.path.join(mcraft,'models','block') and randomize_models:
                blockmodels.append(fullfilepath)
            elif dirpath == os.path.join(mcraft,'blockstates') and randomize_blockstates:
                blockstates.append(fullfilepath)
            elif file.endswith('.ogg') and randomize_sounds:
                sounds.append(fullfilepath)
            elif dirpath == os.path.join(mcraft,'lang') and randomize_text:
                languages.append(fullfilepath)
            elif dirpath == os.path.join(mcraft,'texts') and randomize_text:
                specialtexts.append(fullfilepath)
            elif dirpath == os.path.join(mcraft,'shaders',"post") and randomize_shaders:
                shaders[file.split('.')[1]].append(fullfilepath)
            elif dirpath == os.path.join(os.path.join(data_folder,"assets","realms"),'lang') and randomize_text:
                languages.append(fullfilepath)
            elif dirpath == os.path.join(mcraft,'shaders',"program") and randomize_shaders:
                shaders[file.split('.')[1]].append(fullfilepath)


    logging.warning(f"Random Seed: {seed}")
    def shuffler(randoBool, toRando, inputType):
        if randoBool and toRando != []:
            logging.warning("Randomising "+inputType)
            shufflelist = list(toRando)
            random.shuffle(shufflelist)
            filecount = 0
            while filecount < len(toRando):
                destfile = 'SusThings'
                for newpath in toRando[filecount].split(os.path.sep)[1:]:
                    destfile = os.path.join(destfile,newpath)

                makepath(destfile)
                shutil.copyfile(shufflelist[filecount], destfile)

                #for textures
                mcmeta = shufflelist[filecount]+'.mcmeta'
                mcdest = destfile+'.mcmeta'
                if os.path.exists(mcmeta):
                    shutil.copyfile(mcmeta, mcdest)

                #model file
                #origmodel = textures[texturenum].split('/')[::-1][0].split('.')[0]+'.json'
                #shufmodel = SusThings[texturenum].split('/')[::-1][0].split('.')[0]+'.json'
                #blockpath = '/assets/minecraft/models/block/'
                #itempath = '/assets/minecraft/models/item/'
                #makepath('SusThings'+blockpath)
                #makepath('SusThings'+itempath)
                #if os.path.exists(resourcepack+blockpath+shufmodel):
                #    shutil.copyfile(resourcepack+blockpath+shufmodel, 'SusThings'+blockpath+origmodel)
                #if os.path.exists(resourcepack+itempath+shufmodel):
                #    shutil.copyfile(resourcepack+itempath+shufmodel, 'SusThings'+itempath+origmodel)

                #blockstates
                #statedir = '/assets/minecraft/blockstates/'
                #makepath('SusThings'+statedir)
                #if os.path.exists(resourcepack+statedir+shufmodel):
                #    shutil.copyfile(resourcepack+statedir+shufmodel,'SusThings'+statedir+origmodel)

                filecount += 1
            logging.warning('Randomised '+inputType)

    randoimagery = randomize_textures or randomize_font
    for resolution, imagefiles in images.items():
        shuffler(randoimagery, imagefiles, f"textures ({resolution})")
    shuffler(randomize_models, itemmodels, "item models")  # can reduce more repeat code with a dict (ie unused tags code in data randomiser)
    shuffler(randomize_models, blockmodels, "block models")
    shuffler(randomize_blockstates, blockstates, "block states")
    shuffler(randomize_sounds, sounds, "sounds")
    for key, value in shaders.items():
        shuffler(randomize_shaders, value, f"shaders ({key})")

    if randomize_text and (languages != [] or specialtexts != []):
        logging.warning("Randomising text")
        langvalues = []

        for lang in languages:
            with open(lang, encoding='utf-8') as f:
                data = json.load(f)
            langvalues += list(data.values())

        for tfile in specialtexts:
            with open(tfile, encoding='utf-8') as f:
                content = f.readlines()
            content = [x.strip() for x in content]
            langvalues += content

        processedlangs = 0
        totallangs = len(languages) + len(specialtexts)
        for lang in languages:
            with open(lang, encoding='utf-8') as f:
                data = json.load(f)
            shufflelang = {}
            for key in list(data.keys()):
                randindex = random.randint(0, len(langvalues)-1)
                shufflelang[key] = langvalues[randindex]
                del langvalues[randindex]
            destpath = 'SusThings'+lang[4:]
            makepath(destpath)
            with open(destpath, 'w', encoding='utf-8') as output:
                json.dump(shufflelang, output)

        for tfile in specialtexts:
            with open(tfile, encoding='utf-8') as f:
                content = f.readlines()
            linesadded = 0
            outputlines = []
            while linesadded < len(content):
                randindex = random.randint(0, len(langvalues)-1)
                outputlines.append(langvalues[randindex])
                del langvalues[randindex]
                linesadded += 1
            destpath = 'SusThings'+tfile[4:]
            makepath(destpath)
            with open(destpath, 'w', encoding='utf-8') as output:
                output.write('\n'.join(outputlines))

        logging.warning("Randomised text")

    logging.warning("Creating meta files")
    if "16x16" in images.keys():
        shutil.copyfile(random.choice(images["16x16"]), os.path.join('SusThings','pack.png'))
    elif os.path.exists(os.path.join(data_folder,'pack.png')):
        shutil.copyfile(os.path.join(data_folder,'pack.png'), os.path.join('SusThings','pack.png'))

    makepath(os.path.join('SusThings','pack.mcmeta'))
    with open(os.path.join('SusThings','pack.mcmeta'), "w") as descfile:
        descfile.write('{"pack":{"pack_format":4,"description":"Minecraft Shuffled by lexikiq"}}')
    logging.warning('Installing to resource pack folder')

    try:
        system = sys.platform.lower()
        if system.startswith('lnux'):
            destfolder = os.path.expanduser(os.path.join('~', '.minecraft', 'resourcepacks', 'shuffle'))
        elif system.startswith('darwin'):
            destfolder = os.path.expanduser(os.path.join('~', 'Library', 'Application Support', 'minecraft', 'resourcepacks', 'shuffle'))
        elif system.startswith('wn'):
            destfolder = os.path.expandvars(os.path.join('%APPDATA%', '.minecraft', 'resourcepacks', 'shuffle'))
        else:
            logging.warning('Failed to identify operating system, placing file in current folder instead.')
        destfolder='SusThings'
        shutil.make_archive(destfolder, 'zp', 'SusThings')
        shutil.rmtree('SusThings')
        return 'Resource pack installed!'
    except:
        return 'Compression failed! Please manually move the "SusThings" folder to your resource pack folder.'
print(main())
