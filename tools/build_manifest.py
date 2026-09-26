"""Generate an immutable-download manifest using only Python's standard library."""
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.parse import quote

SERVER_ONLY_MOD_PREFIXES = ('serveurutils-',)


def build(root, repository, commit):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Nom de depot GitHub invalide')
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Commit Git invalide')
    config = json.loads((root / 'pack.json').read_text(encoding='utf-8'))
    if config.get('ready') is not True:
        if (root / 'manifest.json').exists():
            raise ValueError('Un pack deja publie ne peut pas etre desactive silencieusement.')
        print('Pack en preparation : aucun manifeste genere.')
        return None
    if config['versions'] != {'minecraft': '1.21.1', 'neoforge': '21.1.250', 'java': 21}:
        raise ValueError('Versions attendues : Minecraft 1.21.1, NeoForge 21.1.250, Java 21')
    files, seen = [], set()
    for folder in ('mods', 'config', 'defaultconfigs', 'resourcepacks', 'shaderpacks'):
        for path in sorted((root / folder).rglob('*')):
            if path.is_symlink():
                raise ValueError('Lien interdit : ' + str(path))
            if not path.is_file() or path.name in ('README.md', '.gitkeep'):
                continue
            relative = path.relative_to(root).as_posix()
            if folder == 'mods' and path.suffix.lower() != '.jar':
                raise ValueError('Seuls les .jar sont acceptes dans mods : ' + relative)
            # Syncora mirrors server mods into mods/; never distribute server-only code
            # to players even when that external sync adds the file again.
            if folder == 'mods' and path.name.casefold().startswith(SERVER_ONLY_MOD_PREFIXES):
                continue
            for part in relative.split('/'):
                if part.endswith(('.', ' ')) or re.search(r'[<>:"\\|?*\x00-\x1f]', part) or re.match(r'(?i)^(con|prn|aux|nul|com[0-9]|lpt[0-9])(?:\.|$)', part):
                    raise ValueError('Nom incompatible Windows : ' + relative)
            if relative.casefold() in seen:
                raise ValueError('Collision Windows : ' + relative)
            seen.add(relative.casefold())
            size = path.stat().st_size
            if size >= 100 * 1024**2:
                raise ValueError('Fichier trop volumineux pour cette distribution GitHub : ' + relative)
            with path.open('rb') as stream:
                if stream.read(128).startswith(b'version https://git-lfs.github.com/spec'):
                    raise ValueError('Pointeur Git LFS refuse : ' + relative)
                stream.seek(0)
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            files.append({'path': relative, 'url': f'https://raw.githubusercontent.com/{repository}/{commit}/' + quote(relative, safe='/'),
                          'size': size, 'sha256': digest, 'side': 'client',
                          'policy': 'seed' if folder in ('config', 'defaultconfigs') or (folder == 'shaderpacks' and path.suffix == '.txt') else 'enforced'})
    if not any(f['path'].startswith('mods/') for f in files) and not config.get('allowEmptyMods'):
        raise ValueError('Aucun mod : ajoutez les .jar avant de publier le pack.')
    manifest = {k: config[k] for k in ('schemaVersion', 'versions', 'server', 'socials')}
    manifest.update(packVersion=commit, files=files)
    (root / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(files)} fichiers verifies ; manifeste genere.')
    return manifest


if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1], os.environ['GITHUB_REPOSITORY'], os.environ['GITHUB_SHA'])
