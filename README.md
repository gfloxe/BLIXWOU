# BLIXWOU — pack du serveur

Minecraft Java **1.21.10**, NeoForge **21.10.64**.

## Ajouter ou mettre à jour les mods

1. Déposez les fichiers `.jar` destinés aux joueurs dans `mods/`. Remplacez les anciennes versions dans le dépôt ; ne laissez pas deux versions du même mod.
2. Les mods exclusivement serveur vont dans `server-mods/` : ils ne sont pas téléchargés par le launcher.
3. Facultatif : placez les réglages dans `config/`. Ils sont copiés une première fois puis préservés chez le joueur.
4. Validez les fichiers sur la branche `main`. Dans l’onglet **Actions**, attendez que **Publier le pack BLIXWOU** soit vert.
5. L’action produit `manifest.json` automatiquement : nom, taille et SHA-256 exact de chaque fichier. Les téléchargements pointent vers le commit correspondant, afin de ne pas mélanger deux versions.

Le dépôt doit être public pour être téléchargé sans identifiant par les joueurs. Ajoutez uniquement des mods dont vous avez le droit de redistribuer les fichiers. Vérifiez leur compatibilité Minecraft/NeoForge et leurs dépendances. GitHub limite la taille des fichiers : utilisez Git pour les fichiers dépassant la limite de téléversement du site ; les fichiers de 100 Mo ou plus et les pointeurs Git LFS sont refusés par le générateur.

## Premier démarrage

Le dépôt est livré **vide**, avec `ready: false` dans `pack.json`. Ajoutez les mods, puis passez `ready` à `true` une fois le pack complet. Aucun manifeste jouable n’est généré avant cette validation. Pour publier volontairement un pack sans mod, indiquez aussi `allowEmptyMods: true`.

La première publication requiert que GitHub Actions soit autorisé à écrire le contenu du dépôt. Si une politique du compte interdit cette permission, l’action échoue explicitement. La génération du manifeste ne déploie aucun service Azure.

Après publication, communiquez l’URL du dépôt pour brancher le launcher sur :
`https://raw.githubusercontent.com/PROPRIETAIRE/DEPOT/main/manifest.json`

Le launcher vérifie chaque fichier à chaque synchronisation. Un fichier géré modifié, même à taille identique, est remplacé. Un ancien mod géré retiré du dépôt est supprimé pour éviter les doublons. Les sauvegardes, captures et réglages personnels ne font pas partie de cette synchronisation. Les mods ajoutés manuellement qui entrent en conflit sont signalés.
