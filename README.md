# 🛒 Bot de Vendas Discord — Simples

Desenvolvido por **Naoeocask**  
🌐 [Site Oficial](https://naoeocask.github.io/SYNTAXTEAM) | 🎵 [TikTok](https://www.tiktok.com/@syntaxteam_?lang=pt-BR) | 📸 [Instagram](https://www.instagram.com/naoeocask/)

---

> ⚠️ Você pode usar este código livremente, mas **precisa dar créditos** ao autor (`Naoeocask`) em qualquer distribuição.

Este é um **bot de vendas para Discord simples**, feito para facilitar a venda de produtos digitais, licenças, VIPs ou qualquer item que você queira disponibilizar no Discord.  

Os diálogos do bot usam **IA para gerar emojis**, pois alguns PCs podem não ter todos os emojis disponíveis nativamente.  

---

## 💡 Funcionalidades do Bot

- Criação de produtos com SKU, nome, preço, descrição e estoque.
- Venda de produtos via tickets privados no Discord.
- Aprovação ou recusa de compras pela equipe (staff).
- Envio de códigos para clientes automaticamente via DM.
- Configuração de chave PIX, cargo de staff e categoria de tickets.
- Visualização de produtos disponíveis e produtos detalhados para staff.
- Possibilidade de adicionar múltiplos produtos de uma vez.
- Todos os embeds incluem **banner e créditos automáticos** ao autor.

---

## ⚙️ Como Usar

### 1. Pré-requisitos

- Python 3.11 ou superior.
- Biblioteca `discord.py` (ou `py-cord`) instalada.

### 2. Instalar dependências

Use o arquivo `requirements.txt` para instalar tudo de uma vez:

```bash
pip install -r requirements.txt
````

> O `requirements.txt` deve conter todas as bibliotecas necessárias, como:
>
> ```
> discord.py
> ```

### 3. Configurar o bot

No arquivo `main.py`, configure:

```python
DISCORD_TOKEN = "SEU_TOKEN_AQUI"

CONFIG = {
    "nome_loja": "Minha Loja VIP",
    "descricao_painel": "Bem-vindo(a)! Trabalhamos com licenças e VIPs 👑",
    "pix_key": "SUA_CHAVE_PIX",
    "categoria_tickets": "Tickets",
    "banner_url": "URL_DE_IMAGEM_VALIDA",
    "moeda": "R$",
    "canal_feedback": "ID_DO_CANAL_DE_FEEDBACK",
    "cor_embed": 0x00FF00
}
```

* `banner_url` precisa ser um **link de imagem válido**.
* `canal_feedback` é o ID do canal onde o bot envia o registro de compras.

### 4. Executar o bot

No terminal, rode:

```bash
python main.py
```

Se tudo estiver correto, o bot irá:

* Logar no Discord.
* Sincronizar todos os comandos (`slash commands`).
* Ficar pronto para receber pedidos e vendas.

---

## 🛠️ Comandos do Bot

**Para Staff/Admin:**

* `/criar_produto` — Adiciona ou atualiza um produto.
* `/adicionar_estoque` — Adiciona códigos ao estoque de um produto.
* `/postar_painel` — Cria painel de venda de um produto no canal atual.
* `/aprovar` — Aprova ticket e envia código por DM.
* `/recusar` — Recusa ticket.
* `/atualizar_preco` — Atualiza o preço de um produto.
* `/listar_produtos_admin` — Lista produtos detalhado para staff.
* `/definir_pix` — Define a chave PIX do painel.
* `/definir_cargo_staff` — Define o cargo de staff.
* `/definir_categoria_ticket` — Define ou cria categoria de tickets.
* `/remover_produto` — Deleta um produto pelo SKU.
* `/admin_add_varios_produtos` — Adiciona vários produtos de uma vez.

**Para Clientes:**

* `/produtos` — Lista produtos disponíveis para compra.

---

## 📌 Observações

* Todos os embeds possuem **créditos automáticos**: "Desenvolvido por Naoeocask".
* Recomendado ter permissão de administrador para staff que irá aprovar ou recusar pedidos.
* O bot usa **tickets privados** para cada cliente, garantindo privacidade na entrega dos códigos.

---

## 💖 Créditos

Desenvolvido com 💻 por **Naoeocask**
Todos os usuários podem **usar o bot livremente**, desde que dê os devidos créditos.

🌐 Site: [https://naoeocask.github.io/SYNTAXTEAM](https://naoeocask.github.io/SYNTAXTEAM)
🎵 TikTok: [https://www.tiktok.com/@syntaxteam\_?lang=pt-BR](https://www.tiktok.com/@syntaxteam_?lang=pt-BR)
📸 Instagram: [https://www.instagram.com/naoeocask/](https://www.instagram.com/naoeocask/)

---

## ⚡ Aviso

* Diálogos e mensagens são gerados com IA para **garantir compatibilidade de emojis** em diferentes sistemas.
* Sempre use URLs de imagens válidas no `banner_url` para evitar erros de embed.
