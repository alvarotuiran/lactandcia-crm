
# Lactandcia CRM Starter

Aplicación inicial para gestionar clientes, casos de lactancia, seguimientos, tareas y métricas básicas.

## Qué incluye

- Alta de clientas/casos
- Seguimiento por problema
- Estado del caso
- Tareas pendientes
- Dashboard básico
- Biblioteca de recursos recomendados según problema
- Datos guardados en CSV para empezar sin base de datos

## Cómo ejecutarla

1. Instala Python 3.10 o superior.
2. En la carpeta del proyecto, ejecuta:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Siguiente evolución recomendada

1. Migrar CSV a Airtable/Supabase.
2. Añadir autenticación.
3. Integrar WhatsApp Business o email.
4. Automatizar follow-ups.
5. Crear portal privado para madres.
6. Añadir consentimiento RGPD y trazabilidad.
