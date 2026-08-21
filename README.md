# ColdTrack Gateway

Gateway de integración para el prototipo **ColdTrack**, encargado de recibir la telemetría generada por un Arduino UNO simulado en **Tinkercad**, validarla y reenviarla mediante HTTP a una API local de ColdTrack.

El objetivo de este repositorio es permitir probar el flujo completo sin necesidad de disponer de hardware físico.

```text
Sensores simulados
      ↓
Arduino UNO en Tinkercad
      ↓
Monitor Serie (JSON)
      ↓
tinkercad-serial-bridge
      ↓
ColdTrack Gateway (Python / Flask) :8080
      ↓
HTTP POST
      ↓
ColdTrack API (Python / Flask) :5000
