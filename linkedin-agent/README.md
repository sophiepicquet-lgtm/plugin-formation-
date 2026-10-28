# Plugin « LinkedIn Agent » (11 compétences Claude)

Copie, sans modification, du dépôt public
[Jakeschincariol/linkedin-agent-skill](https://github.com/Jakeschincariol/linkedin-agent-skill)
de Jake Schincariol, version 1.0 (commit `add2c23` du 7 septembre 2026).
Licence MIT : voir `LICENSE`. Le README d'origine, en anglais, est dans `README-original-EN.md`.

## Contenu

| Commande | Rôle |
| --- | --- |
| `/li-post` | Transforme une idée en post : 3 accroches (21 formules), un brouillon complet |
| `/li-comment` | Rédige un commentaire sur le post de quelqu'un d'autre |
| `/li-reply` | Trie et rédige les réponses aux commentaires sous tes posts |
| `/li-profile` | Note le profil sur 100 (grille de 12 critères) et propose les réécritures |
| `/li-plan` | Planning de la semaine : quoi publier, quand, avec qui interagir |
| `/li-human` | Nettoie un brouillon (2 scripts Python locaux) et lui donne un score |
| `/li-carousel` | Texte d'un carrousel diapo par diapo |
| `/li-repurpose` | Décline une vidéo, une newsletter ou une transcription en plusieurs posts |
| `/li-dm` | Note d'invitation, premier message et deux relances |
| `/li-inbox` | Trie les messages reçus |
| `/li-audit` | Bilan des posts déjà publiés |

Aucune compétence ne publie sur LinkedIn : chacune se termine par un texte à copier-coller.

## Vérification (27 octobre 2026)

- Les deux scripts Python (`li-human`) n'utilisent que la bibliothèque standard,
  ne font aucun appel réseau et ne lancent aucune commande système.
- Les 11 fichiers `SKILL.md` ont un en-tête valide ; les 3 fichiers JSON sont valides.

## Adaptation française de `li-human` (version 1.1.0, 27 octobre 2026)

Seule modification apportée au dépôt d'origine. Le comportement en anglais est inchangé :
sorties identiques à l'original, vérifiées sur trois textes de test.

- **Détection automatique du français** (ou option `--lang fr`), avec un lexique dédié : `slop_fr.json`.
- **Typographie française respectée** : les espaces insécables sont conservées, et ajoutées si
  elles manquent avant « : ; ! ? » et dans « ». Les apostrophes ’ sont conservées, et “ ” devient « ».
  Les heures (14:30), les smileys, les liens et les adresses e-mail ne sont pas touchés.
- **Lexique français** : 59 expressions typiques des textes générés (« dans un monde en constante
  évolution », « il est crucial de », « n'hésitez pas à »...). Les mots dont le remplacement
  casserait l'accord (levier, écosystème, incontournable...) sont signalés, pas remplacés.
- **12 tics de structure français signalés** : « Ce n'est pas juste X, c'est Y », « Le résultat ? »,
  « Et vous ? », énumérations en trois temps...
- **Scores adaptés au français** : ’ « » et les espaces insécables ne comptent plus comme
  « empreinte » IA, et le contrôle VOICE ignore les élisions (j', l', c'), obligatoires en français.

Ces scores restent des repères locaux, pas un verdict de détecteur.

## Limite restante

Plusieurs compétences lisent ou écrivent `~/.claude/linkedin/voice.md`, `log.md` et `plan.md`
(dossier de Claude Code). Dans l'application Claude, coller son `voice.md` dans la conversation.

## Mise en route

Remplir `templates/voice.md` (ton, vocabulaire, cibles), ou coller trois de ses posts dans Claude
en demandant : « écris mon voice.md à partir de ces posts ».
