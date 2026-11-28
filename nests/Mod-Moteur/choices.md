## Open decisions

## Projects on hold

### Code de sortie de `verify_passes123.py`

La suite affiche ses échecs mais ressort toujours avec le code `0` : un enchaînement automatisé ne peut détecter un échec qu'en lisant la ligne `VERIFICATION SUMMARY`. Faire ressortir le script avec un code différent de `0` en cas d'échec ; aucun script de `tools/` ne l'appelle aujourd'hui, seule la documentation des autres nids mentionne le comportement actuel.
