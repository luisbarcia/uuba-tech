# UUBA Recebe — Mapa de Dependencias

```
Modulo 0 (Multi-tenancy) ---> BLOQUEIA TUDO
  |
  |---> Modulo 1 (Clientes/Devedores) ---> Modulo 2 (Faturas/Recebiveis)
  |       |                                   |
  |       |                                   |---> Modulo 3 (Pre-delinquency)
  |       |                                   |       [precisa de: faturas com vencimento futuro]
  |       |                                   |
  |       |                                   |---> Modulo 4 (Regua de Cobranca)
  |       |                                   |       [precisa de: faturas vencidas]
  |       |                                   |       [compliance embutido — nao e modulo separado]
  |       |                                   |       |
  |       |                                   |       |---> Modulo 5 (Bot IA Conversacional)
  |       |                                   |               [precisa de: regua + faturas + clientes]
  |       |                                   |
  |       |                                   |---> Modulo 7 (Portal do Devedor)
  |       |                                           [precisa de: faturas + integracao pagamento]
  |       |
  |       |---> Modulo 6 (Import de Titulos)
  |               [precisa de: clientes + faturas para criar/atualizar]
  |
  |---> Integracoes Externas
  |       |---> Conta Azul (pagamentos) ---> usado por Modulos 2, 4, 7
  |       |---> Evolution API (WhatsApp) ---> usado por Modulos 4, 5
  |       |---> Claude API (IA) ---> usado por Modulo 5
  |       |---> Chatwoot (atendimento) ---> usado por Modulos 5, 7
  |
  |---> Modulo 8 (Dashboard e Analytics)
  |       [precisa de: dados de todos os modulos — implementar apos Modulos 1-7]
  |
  |---> Modulo 9 (Scoring e Inteligencia)
  |       [precisa de: dados historicos — implementar apos ter volume de dados]
  |
  |---> Modulo 10 (Resiliencia e Self-Healing)
          [permeia todos — implementar componentes junto com cada modulo]
```

### Ordem recomendada de implementacao

1. **Fase 1 -- Fundacao:** Modulo 0 (Multi-tenancy) + Integracoes Externas (Conta Azul, Evolution API)
2. **Fase 2 -- Core:** Modulos 1 (Clientes) + 2 (Faturas) + 6 (Import)
3. **Fase 3 -- Cobranca:** Modulos 3 (Pre-delinquency) + 4 (Regua) + 5 (Bot IA)
4. **Fase 4 -- Devedor:** Modulo 7 (Portal do Devedor)
5. **Fase 5 -- Inteligencia:** Modulos 8 (Dashboard) + 9 (Scoring)
6. **Continuo:** Modulo 10 (Resiliencia) -- implementado incrementalmente em cada fase
