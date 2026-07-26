# Molecular Intelligence Guide

`engines/chemistry_intelligence/molecular_models.py` supplies **metadata hooks** only.

## Representation hooks

Molecules, compounds, chemical formulae, structural formulae, Lewis / electron-dot diagrams, bond angles, hybridization, functional groups, crystal structures, 3D molecular viewers.

## Rules

- Formula candidates are extracted heuristically from source text / chemical equation passthrough  
- Rendering and interaction belong to LXP / VMLE  
- Do not invent structures not present or implied by verified lesson content  
- Computation Layer (RDKit / mhchem) remains the source of verified molecular artifacts when attached to ULI STEM  

## ULIQE

Molecular representation coverage contributes to CIP teaching signals (`molecular_representation`) without altering certify rules.
