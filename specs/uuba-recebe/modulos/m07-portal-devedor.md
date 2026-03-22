# Modulo 7: Portal do Devedor

**Status:** Nao implementado

### Functional Requirements

**FR-074: Acesso via link unico com JWT RS256**
When o devedor recebe uma mensagem de cobranca, the system shall incluir link unico contendo token JWT assinado com RS256 (chave assimetrica). O token deve conter: `devedor_id`, `tenant_id`, `exp` (72h), e `iat`. O sistema deve expor endpoint de revogacao `POST /api/v1/portal/tokens/revoke` que adiciona o token a uma blacklist (Redis com TTL igual ao tempo restante de expiracao).

**FR-075: Verificacao secundaria no primeiro acesso**
When o devedor acessa o portal pela primeira vez com um token valido, the system shall solicitar os ultimos 4 digitos do CPF como verificacao secundaria antes de exibir qualquer dado financeiro. Apos verificacao bem-sucedida, o sistema emite cookie de sessao para acessos subsequentes com o mesmo token.

**FR-076: Consulta de faturas**
The portal shall exibir lista de faturas do devedor com: valor, vencimento, status, dias de atraso, e opcoes de acao (pagar, negociar).

**FR-077: Pagamento online (Pix e boleto)**
Where o devedor clica em "Pagar", the portal shall exibir opcoes de pagamento: Pix (QR code com validade de 30 minutos) e boleto bancario (via Conta Azul).

**FR-078: Regeneracao automatica de QR code Pix**
Where o QR code Pix expirou (30 minutos), the portal shall detectar a expiracao e gerar automaticamente um novo QR code sem necessidade de acao do devedor, exibindo mensagem "QR code atualizado".

**FR-079: Negociacao de acordo**
Where a empresa habilitou negociacao no portal, the devedor shall poder solicitar parcelamento ou desconto dentro dos limites pre-configurados. Opcoes apresentadas automaticamente (ex: "Pague hoje com 5% de desconto" ou "Parcele em 3x sem juros").

**FR-080: Historico de acordos**
The portal shall exibir historico de acordos anteriores, parcelas pagas, e comprovantes de pagamento.

**FR-081: Chat com atendente**
Where o devedor precisa de atendimento humano, the portal shall oferecer chat integrado ao Chatwoot para conversar com a equipe de cobranca.

**FR-082: Responsividade mobile-first**
The portal shall ser totalmente responsivo (mobile-first) pois a maioria dos acessos vira via link no WhatsApp em dispositivos moveis.

**FR-083: Solicitacao de novo link quando expirado**
Where o token JWT expirou, the portal shall exibir mensagem "Link expirado" e opcao de solicitar novo link. Ao solicitar, o sistema envia novo link via WhatsApp para o numero cadastrado do devedor.

**FR-084: Rate limit para re-geracao de links**
The system shall limitar a re-geracao de links do portal a no maximo 3 por dia por devedor. Apos atingir o limite, exibir mensagem "Limite de solicitacoes atingido. Tente novamente amanha ou entre em contato pelo WhatsApp."

**FR-085: Roteamento multi-tenant no portal**
When o devedor acessa o portal, the system shall identificar o tenant via `tenant_id` embutido no JWT e rotear para os dados corretos, aplicando branding basico do tenant (logo e nome da empresa).

**FR-086: Seguranca do portal (CSP, HSTS, anti-phishing)**
The portal shall implementar: Content Security Policy (CSP) restritivo, HTTP Strict Transport Security (HSTS) com max-age de 1 ano, X-Content-Type-Options: nosniff, X-Frame-Options: DENY, e Referrer-Policy: strict-origin-when-cross-origin.

**FR-087: Fallback HTML basico**
Where o browser do devedor nao suporta JavaScript moderno (ES2015+), the portal shall renderizar versao HTML basica server-side com funcionalidades essenciais: visualizar faturas, copiar codigo Pix, e acessar link de boleto.

### Acceptance Criteria

**AC-068: Acesso via link no WhatsApp**
Given o devedor recebe mensagem com link do portal contendo JWT valido,
When clica no link no celular,
Then o portal solicita os ultimos 4 digitos do CPF,
And apos verificacao correta, exibe suas faturas em aberto.

**AC-069: Verificacao CPF bloqueia acesso indevido**
Given um link do portal e compartilhado com terceiro que nao conhece o CPF do devedor,
When o terceiro tenta acessar e insere digitos incorretos do CPF,
Then o portal exibe "Verificacao falhou" e nao exibe dados financeiros,
And apos 5 tentativas incorretas, o token e revogado automaticamente.

**AC-070: Pagamento Pix pelo portal**
Given o devedor esta no portal com fatura de R$ 500,00,
When clica em "Pagar com Pix",
Then um QR code e exibido com valor de R$ 500,00 e validade de 30 minutos,
And apos pagamento confirmado via webhook, o status atualiza na tela.

**AC-071: QR code Pix expira antes do pagamento**
Given o devedor esta visualizando QR code Pix que expirou (30 minutos),
When o timer de expiracao e atingido,
Then o portal gera automaticamente novo QR code sem acao do devedor,
And exibe mensagem "QR code atualizado — escaneie novamente".

**AC-072: Negociacao de desconto no portal**
Given a regra permite ate 10% de desconto para pagamento a vista,
When o devedor acessa fatura de R$ 1.000,00,
Then o portal exibe: "Pague hoje por R$ 900,00 (10% de desconto)".

**AC-073: Link expirado com solicitacao de novo**
Given o token do link tem validade de 72h e o devedor acessa apos 72h,
When o portal detecta token expirado,
Then exibe mensagem "Link expirado" e botao "Solicitar novo link via WhatsApp",
And ao clicar, novo link e enviado para o numero cadastrado do devedor.

**AC-074: Devedor abre em dois dispositivos**
Given o devedor abre o portal em dois dispositivos simultaneamente (celular e computador),
When ambas as sessoes estao ativas,
Then ambas funcionam normalmente pois a sessao e stateless (JWT),
And operacoes de pagamento sao idempotentes (mesmo pagamento nao duplica).

**AC-075: Browser antigo sem JavaScript moderno**
Given o devedor acessa o portal com browser que nao suporta ES2015+,
When a pagina carrega,
Then renderiza versao HTML basica server-side,
And o devedor consegue visualizar faturas e copiar codigo Pix copia-e-cola.

**AC-076: Rate limit de re-geracao de links**
Given o devedor ja solicitou 3 novos links no mesmo dia,
When tenta solicitar o 4o link,
Then o sistema exibe "Limite de solicitacoes atingido. Tente novamente amanha ou entre em contato pelo WhatsApp."
