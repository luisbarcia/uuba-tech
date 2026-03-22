# UUBA Recebe — Out of Scope (v1)

Os seguintes items estao explicitamente fora do escopo da v1 e planejados para versoes futuras:

| Item | Motivo | Versao planejada |
|------|--------|------------------|
| Canais alem do WhatsApp (email, SMS, voz) | Complexidade de integracao, WhatsApp e canal dominante no BR | v2 |
| Integracoes nativas com ERPs especificos (Omie, Bling, SAP) | MVP usa import CSV/API; integracao nativa requer parceria | v2 |
| Cobranca juridica (protestos, negativacao SPC/Serasa) | Requer parceria com bureaus e processos legais | v2/v3 |
| White-label completo (branding customizado por tenant) | Futuro com UUBA Parceiros; v1 tem branding basico (logo + nome) | v2 |
| App mobile nativo | Portal web responsivo e suficiente para v1 | v3 |
| Voicebot (chamadas com IA de voz) | Complexidade de infra + custo de telefonia | v3 |
| Open Banking/Open Finance | Regulamentacao ainda em evolucao, integracao custosa | v2/v3 |
| ML real para scoring | Requer >10k devedores com historico; v1 usa heuristico | v2 |
| Multi-idioma | 100% dos clientes v1 sao brasileiros | v3 |
| DB-per-tenant | Shared DB com tenant_id e suficiente para 100 tenants; DB-per-tenant escala melhor para 500+ | v2/v3 |
| Import recorrente via ERP (sync automatico) | Depende de integracao nativa com ERPs | v2 |
| Resposta em audio (TTS) | Transcricao (receber) e prioridade; gerar audio e futuro | v2 |
