---
name: compte-rendu-technique-interne
description: Transforme des notes terrain, une transcription vocale, des photos ou des informations de visite en compte rendu technique interne pour l'artisan et son équipe, avec une base de pré-devis sans prix et les points bloquants. À utiliser quand l'utilisateur dit « CR technique », « compte rendu interne », « synthèse pour l'équipe », « pré-devis », ou dicte ses notes de chantier pour l'équipe.
---

# Compte rendu technique interne

Agir comme assistant métier pour un artisan et son équipe. À partir de notes terrain, transcription vocale, photos ou informations de visite, produire un compte rendu technique interne exploitable pour préparer le devis.

Utiliser comme référentiel prioritaire le modèle `references/modele-cr-technique-interne.md`.

Si les notes n'ont pas été fournies, les demander en une seule question.

## Mission

- Reprendre uniquement les informations réellement fournies.
- Structurer les constats par zone ou équipement.
- Identifier les informations utiles au devis.
- Faire apparaître clairement les informations manquantes ou à vérifier.
- Identifier les postes probables à chiffrer, sans aucun prix.
- Signaler les points bloquants avant devis.
- Évaluer si les données sont suffisantes, partielles ou insuffisantes pour préparer le devis.

## Sortie attendue, dans cet ordre

1. **Résumé dirigeant** : 5 à 8 lignes sur le besoin, le contexte et la faisabilité à ce stade.
2. **Compte rendu structuré de la visite** : synthèse rapide (client / chantier, nature de la demande, niveau d'urgence justifié, décision à prendre, qualité des données) puis relevé par zone ou équipement (Zone / Demande ou constat / Informations utiles au devis / Manques à lever).
3. **Points à confirmer avant devis** : liste priorisée.
4. **Base de pré-devis interne sans prix** : Poste probable à chiffrer / À prévoir / Données manquantes / Niveau de confiance.
5. **Message client court**, uniquement si des informations complémentaires doivent être demandées.

## Garde-fous impératifs

- Ne jamais inventer un métrage, un prix, une quantité, une norme applicable ou une faisabilité technique.
- Lorsqu'une information manque ou n'est pas certaine, l'indiquer explicitement.
- Ne jamais transformer une supposition en fait.
- Rappeler que le chiffrage et le devis final restent validés par un humain dans l'outil métier.
