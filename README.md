# Blender Draco Compression CLI

Compresse tes fichiers 3D avec la compression Draco directement en ligne de commande en utilisant Blender.

## Installation

### 1. Installer Blender

Telecharge et installe Blender depuis [blender.org](https://www.blender.org/download/)

- Versions supportees: 2.93+
- Recommended: Blender 3.6+ ou 4.x

### 2. Cloner le projet

```bash
git clone https://github.com/username/cli-draco-compression.git
cd cli-draco-compression
```

### 3. (Optionnel) Ajouter au PATH

Pour utiliser les commandes depuis n'importe quel repertoire.

**Windows:**
```powershell
# Ajouter au PATH utilisateur
setx PATH "$env:PATH;C:\chemin\vers\cli-draco-compression"

# Ou utiliser le chemin complet
& "C:\chemin\vers\cli-draco-compression\blender_draco.bat" model.glb
```

**Linux/macOS:**
```bash
# Rendre executable et ajouter au PATH
chmod +x blender_draco.sh
sudo ln -s "$(pwd)/blender_draco.sh" /usr/local/bin/blender-draco
```

---

## Utilisation Rapide

### Mode Simple (tout par defaut)

Le moyen le plus rapide - genere `model_compressed.glb` automatiquement.

**Windows:**
```bat
blender_draco.bat model.glb
```

**Python:**
```bash
python blender_draco.py model.glb
```

**Directement avec Blender:**
```bash
blender --background --python compress.py -- model.glb
```

**Resultat:** `model_compressed.glb`
- Draco compression: niveau 7
- Resize textures: active (512px max)
- Format: GLB (1 seul fichier avec tout embarqué)

---

## Options CLI

| Option | Alias | Defaut | Description |
|--------|-------|--------|-------------|
| `input` | `-i` | (requis) | Fichier d'entree |
| `-o` | `--output` | `*_compressed.glb` | Fichier de sortie |
| `--draco-level` | | `7` | Niveau de compression Draco (0-10) |
| `--resize-textures` | | **active** | Active le resize des textures |
| `--no-resize` | | | Desactive le resize des textures |
| `--texture-size` | | `512` | Taille max textures (pixels) |
| `--batch` | `-b` | | Mode batch (repertoire) |
| `--output-dir` | `-d` | | Repertoire de sortie (batch) |
| `--format` | `-f` | `glb` | Format: `glb` (1 fichier) ou `gltf` (fichiers separes) |
| `-q` | `--quiet` | | Mode silencieux |
| `-h` | `--help` | | Aide |

---

## Examples

### Compression simple
```bash
blender_draco.bat model.glb
# Output: model_compressed.glb (1 seul fichier)
```

### Avec options personnalisees
```bash
# Compression maximale
python blender_draco.py model.glb --draco-level 10

# Desactiver le resize des textures
blender_draco.bat model.glb --no-resize

# Taille de textures personnalisee
python blender_draco.py model.glb --texture-size 2048

# Format gltf (fichiers separes)
blender_draco.bat model.glb --format gltf
```

### Mode Avance
```bash
# Fichier d'entree et sortie specifies
python blender_draco.py -i model.glb -o optimized.glb --draco-level 8

# Toutes les options
blender_draco.bat -i model.glb -o output.glb --draco-level 10 --texture-size 1024
```

### Mode Batch
```bash
# Traiter tous les fichiers d'un repertoire
python blender_draco.py --batch ./models/

# Avec repertoire de sortie
blender_draco.bat --batch ./models/ --output-dir ./compressed/

# Batch avec options
python blender_draco.py --batch ./models/ --output-dir ./compressed/ --draco-level 7
```

---

## Formats Supportes

### Formats d'entree

| Format | Extension | Description |
|--------|----------|-------------|
| glTF | `.glb`, `.gltf` | Format natif (recommande) |
| Wavefront | `.obj` | Format commun |
| Stanford PLY | `.ply` | Format de maillages |
| STL | `.stl` | Stereolithographie |
| X3D | `.x3d`, `.wrl` | Web 3D |
| COLLADA | `.dae` | Format d'echange |
| FBX | `.fbx` | Filmbox (si supporte par Blender) |
| 3DS | `.3ds` | 3D Studio |

### Formats de sortie

| Format | Extension | Description |
|--------|----------|-------------|
| **GLB** | `.glb` | 1 seul fichier (recommande) |
| GLTF | `.gltf` + `.bin` + textures | Fichiers separes |

---

## Details des Options

### Draco Level (--draco-level)

Niveau de compression Draco (0 = aucune compression, 10 = maximum).

| Niveau | Compression | Qualite | Usage |
|--------|-------------|---------|-------|
| 0 | Aucune | 100% | Test |
| 1-3 | Legere | Tres haute | Preview |
| 4-6 | Moyenne | Haute | Web |
| 7-8 | Forte | Bonne | **Recommande** |
| 9-10 | Maximale | Correcte | Fichiers tres volumineux |

**Defaut: 7**

### Resize Textures (--texture-size)

Redimensionne automatiquement les textures a une taille maximale.

| Taille | Usage |
|--------|-------|
| 256 | Mobile, low-end |
| 512 | **Web standard** |
| 1024 | Desktop, haute qualite |
| 2048+ | Usage specialise |

**Defaut: 512**

---

## Environment

### Variables d'environnement

| Variable | Description |
|----------|-------------|
| `BLENDER_PATH` | Chemin personnalise vers l'executable Blender |

**Exemple:**
```bash
# Windows
set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.0\blender.exe

# Linux/macOS
export BLENDER_PATH=/usr/bin/blender
```

---

## Troubleshooting

### "Blender not found"

1. Verifie que Blender est installe
2. Utilise `BLENDER_PATH` pour specifier le chemin
3. Ajoute Blender au PATH systeme

### "No objects imported"

- Verifie que le fichier d'entree existe
- Verifie que le format est supporte
- Essaie d'ouvrir le fichier dans Blender manuellement

### Erreur de compression

- Certains fichiers peuvent avoir des problemes de compatibilite
- Essaie avec `--no-resize` pour isoler le probleme
- Verifie les logs pour plus de details

### Probleme de permissions (Linux/macOS)

```bash
chmod +x blender_draco.sh
chmod +x compress.py
```

---

## Performance

- Temps de traitement: ~1-5 secondes par fichier (depend de la complexite)
- Memoire: Blender utilise ~500MB minimum
- Batch: Traite les fichiers sequentiellement

---

## License

MIT License - Libre d'utilisation et de modification.

---

## Credits

- Compression Draco: [Google Draco](https://google.github.io/draco/)
- Format glTF: [Khronos Group](https://www.khronos.org/gltf/)
- Script: Personalite utilise Blender Python API
