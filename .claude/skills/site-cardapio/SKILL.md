---
name: site-cardapio
description: Cria cardápio digital responsivo para restaurantes/lanchonetes, com categorias, carrinho e pedido enviado pronto para o WhatsApp. Use quando pedirem cardápio digital ou site de delivery.
---
1. Colete: nome, logo, cores, WhatsApp (com DDD), endereço, horário, taxa de entrega, categorias e itens (nome, descrição, preço, foto).
2. Gere um único `index.html` (+ imagens) mobile-first: cabeçalho com status aberto/fechado pelo horário, abas de categoria, cards de item com "+", carrinho fixo no rodapé, campo de nome/endereço/observação, botão que abre `https://wa.me/55NUMERO?text=` com o pedido formatado (itens, quantidades, total).
3. SEO local: `<title>`, meta description, Open Graph com foto, Schema.org `Restaurant`.
4. Teste no tamanho 390x844 com Playwright e confira o texto da mensagem gerada.
5. Deploy: Cloudflare Pages/Workers ou GitHub Pages; entregue o link ao Mathias para aprovação antes de mandar ao cliente.
