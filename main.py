"""
Desenvolvido por Naoeocask
© 2025 Naoeocask

Você pode usar este código livremente, desde que dê os devidos créditos ao autor.
"""

import json
import os
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

import discord
from discord import app_commands
from discord.ext import commands

CONFIG = {
    "nome_loja": "Minha Loja VIP",
    "descricao_painel": "Bem-vindo(a)! Trabalhamos com licenças e VIPs 👑",
    "pix_key": "11978863353",
    "categoria_tickets": "Tickets",
    "banner_url": "COLOQUE SUA URL",
    "moeda": "R$",
    "canal_feedback": "COLOQUE O CANAL DE FEEDBACK",  
    "cor_embed": 0x00FF00
}

DISCORD_TOKEN = "TOKEN DO SEU BOT AQUI"

DATA_DIR = "data"
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default

def save_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

products: Dict[str, Dict[str, Any]] = load_json(PRODUCTS_FILE, {})
persisted_config: Dict[str, Any] = load_json(CONFIG_FILE, {})
persisted_config.update(CONFIG)
save_json(CONFIG_FILE, persisted_config)


@dataclass
class Produto:
    sku: str
    nome: str
    preco: float
    descricao: str
    stock: List[str]

    @staticmethod
    def from_dict(sku: str, d: Dict[str, Any]) -> "Produto":
        return Produto(
            sku=sku,
            nome=d.get("nome", sku),
            preco=float(d.get("preco", 0.0)),
            descricao=d.get("descricao", ""),
            stock=list(d.get("stock", [])),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nome": self.nome,
            "preco": self.preco,
            "descricao": self.descricao,
            "stock": self.stock,
        }

def get_produto(sku: str) -> Optional[Produto]:
    data = products.get(sku)
    if not data:
        return None
    return Produto.from_dict(sku, data)

def set_produto(p: Produto) -> None:
    products[p.sku] = p.to_dict()
    save_json(PRODUCTS_FILE, products)


def staff_role_name() -> str:
    return persisted_config.get("cargo_staff", "Vendedor")

def moeda() -> str:
    return persisted_config.get("moeda", "R$")

def cor_embed() -> int:
    return int(persisted_config.get("cor_embed", CONFIG["cor_embed"]))

def pix_key() -> str:
    return persisted_config.get("pix_key", "")

def tickets_category_name() -> str:
    return persisted_config.get("categoria_tickets", "Tickets")

def loja_nome() -> str:
    return persisted_config.get("nome_loja", "Minha Loja")

def banner_url() -> Optional[str]:
    return persisted_config.get("banner_url") or None

def canal_feedback_id() -> int:
    return int(persisted_config.get("canal_feedback", 0))

async def ensure_tickets_category(guild: discord.Guild) -> Optional[discord.CategoryChannel]:
    cat_name = tickets_category_name()
    category = discord.utils.get(guild.categories, name=cat_name)
    if category is None:
        try:
            category = await guild.create_category(cat_name, reason="Categoria de Tickets (bot)")
        except discord.Forbidden:
            return None
    return category

def user_is_staff(member: discord.Member) -> bool:
    if member.guild_permissions.administrator:
        return True
    role = discord.utils.get(member.roles, name=staff_role_name())
    return role is not None

async def send_dm_safe(user: discord.User | discord.Member, embed: discord.Embed, content: Optional[str] = None):
    try:
        return await user.send(content=content, embed=embed)
    except discord.Forbidden:
        return None

async def enviar_feedback_embed(user: discord.Member, produto: Produto, codigo: str):
    canal_id = canal_feedback_id()
    if canal_id == 0:
        return
    canal = user.guild.get_channel(canal_id)
    if not canal:
        return
    embed = criar_embed(
        title="🛒 Compra Realizada",
        description=(
    f"**Cliente:** {user.mention}\n"
    f"**Produto:** {produto.nome}\n"
    f"**Preço:** {moeda()} {produto.preco:,.2f}"

        ),
        color=0x00FF00
    )
    if banner_url():
        embed.set_thumbnail(url=banner_url())
    await canal.send(embed=embed)

def criar_embed(title: str, description: str, color: int = cor_embed()) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="Desenvolvido por naoeocask | github.com/naoeocask",
                     icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png")
    return embed



intents = discord.Intents.default()
intents.members = True
intents.message_content = False

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree
active_tickets: Dict[int, Dict[str, int | str]] = {}


class ComprarView(discord.ui.View):
    def __init__(self, sku: str):
        super().__init__(timeout=None)
        self.sku = sku

class ComprarView(discord.ui.View):
    def __init__(self, sku: str):
        super().__init__(timeout=None) 
        self.sku = sku

    @discord.ui.button(
        label="📩 Comprar",
        style=discord.ButtonStyle.primary,
        custom_id="comprar_button"
    )
    async def comprar(self, interaction: discord.Interaction, button: discord.ui.Button):
        produto = get_produto(self.sku)

        if not produto:
            await interaction.response.send_message("❌ Produto não encontrado.", ephemeral=True)
            return

        for ch_id, info in active_tickets.items():
            if info.get("user_id") == interaction.user.id and info.get("sku") == produto.sku:
                ch = interaction.guild.get_channel(ch_id)
                if ch:
                    await interaction.response.send_message(
                        f"⚠️ Você já tem um ticket aberto: {ch.mention}", ephemeral=True
                    )
                    return

        await interaction.response.defer(ephemeral=True)

        category = await ensure_tickets_category(interaction.guild)
        if not category:
            await interaction.followup.send("❌ Não consegui criar/achar a categoria de Tickets.", ephemeral=True)
            return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        staff_role = discord.utils.get(interaction.guild.roles, name=staff_role_name())
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        channel_name = f"ticket-{interaction.user.name[:16]}-{produto.sku}".lower()
        ticket_channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"Ticket de {interaction.user.id} | SKU={produto.sku}"
        )

        active_tickets[ticket_channel.id] = {"user_id": interaction.user.id, "sku": produto.sku}

        embed = criar_embed(
            title=f"🎫 Ticket de Compra — {produto.nome}",
            description=(
                f"**Preço:** {moeda()} {produto.preco:,.2f}\n"
                f"**Produto:** `{produto.nome}`\n\n"
                f"**Instruções:**\n"
                f"1. Faça o pagamento via PIX: `{pix_key()}`\n"
                f"2. Envie o comprovante neste canal.\n"
                f"3. Aguarde aprovação da staff."
            ),
            color=cor_embed()
        )
        if banner_url():
            embed.set_image(url=banner_url())

        await ticket_channel.send(content=interaction.user.mention, embed=embed)
        await interaction.followup.send(f"✅ Ticket criado: {ticket_channel.mention}", ephemeral=True)


@bot.event
async def on_ready():
    for sku in list(products.keys()):
        bot.add_view(ComprarView(sku))
    try:
        synced = await tree.sync()
        print(f"[OK] Slash commands sincronizados ({len(synced)})")
    except Exception as e:
        print("Erro ao sincronizar comandos:", e)
    print(f"Logado como {bot.user} (ID: {bot.user.id})")

def admin_only():
    def predicate(interaction: discord.Interaction) -> bool:
        return user_is_staff(interaction.user) if isinstance(interaction.user, discord.Member) else False
    return app_commands.check(predicate)

@tree.command(name="produtos", description="Lista produtos disponíveis")
async def produtos_cmd(interaction: discord.Interaction):
    if not products:
        await interaction.response.send_message("Ainda não há produtos cadastrados.", ephemeral=True)
        return

    desc = []
    for sku, data in products.items():
        p = Produto.from_dict(sku, data)
        desc.append(f"**{p.nome}** — `{sku}`\nPreço: {moeda()} {p.preco:,.2f} | Estoque: **{len(p.stock)}**\n")

    embed = criar_embed(
        title=f"🛒 Produtos — {loja_nome()}",
        description="\n".join(desc),
        color=cor_embed()
    )
    if banner_url():
        embed.set_thumbnail(url=banner_url())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="criar_produto", description="Adiciona/atualiza um produto")
@admin_only()
@app_commands.describe(
    sku="Identificador único (ex: LOJA1X)",
    nome="Nome exibido",
    preco="Preço (ex: 99.90)",
    descricao="Descrição curta do produto"
)
async def admin_add_produto(interaction: discord.Interaction, sku: str, nome: str, preco: float, descricao: str):
    sku = sku.upper()
    p = get_produto(sku) or Produto(sku=sku, nome=nome, preco=preco, descricao=descricao, stock=[])
    p.nome = nome
    p.preco = preco
    p.descricao = descricao
    set_produto(p)
    bot.add_view(ComprarView(p.sku))
    await interaction.response.send_message(f"✅ Produto **{p.nome}** (`{p.sku}`) salvo. Estoque: {len(p.stock)}", ephemeral=True)

@tree.command(name="adicionar_estoque", description="Adiciona código(s) ao estoque de um SKU")
@admin_only()
@app_commands.describe(sku="SKU", codigo="Código(s) separados por linha")
async def admin_add_estoque(interaction: discord.Interaction, sku: str, codigo: str):
    p = get_produto(sku.upper())
    if not p:
        await interaction.response.send_message("❌ SKU não encontrado.", ephemeral=True)
        return
    novos = [c.strip() for c in codigo.splitlines() if c.strip()]
    p.stock.extend(novos)
    set_produto(p)
    await interaction.response.send_message(f"✅ Adicionados {len(novos)} código(s) ao estoque de `{p.sku}`. Total: {len(p.stock)}", ephemeral=True)

@tree.command(name="postar_painel", description="Cria um painel de venda para um SKU no canal atual")
@admin_only()
@app_commands.describe(sku="SKU do produto")
async def admin_painel(interaction: discord.Interaction, sku: str):
    produto = get_produto(sku.upper())
    if not produto:
        await interaction.response.send_message("❌ SKU não encontrado.", ephemeral=True)
        return

    embed = criar_embed(
        title=f"🛍️ {produto.nome}",
        description=(
            f"{produto.descricao}\n\n"
            f"**Preço:** {moeda()} {produto.preco:,.2f}\n"
            f"**Estoque:** **{len(produto.stock)}**\n"
            f"**SKU:** `{produto.sku}`\n\n"
            f"Clique em **Comprar** para abrir um ticket privado."
        ),
        color=cor_embed()
    )
    if banner_url():
        embed.set_image(url=banner_url())

    view = ComprarView(produto.sku)
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="atualizar_preco", description="Atualiza preço de um produto")
@admin_only()
@app_commands.describe(sku="SKU", preco="Novo preço")
async def admin_set_preco(interaction: discord.Interaction, sku: str, preco: float):
    p = get_produto(sku.upper())
    if not p:
        await interaction.response.send_message("❌ SKU não encontrado.", ephemeral=True)
        return
    p.preco = preco
    set_produto(p)
    await interaction.response.send_message(f"✅ Preço atualizado para {moeda()} {p.preco:,.2f} em `{p.sku}`.", ephemeral=True)

@tree.command(name="listar_produtos_admin", description="Lista todos os produtos (detalhado para staff)")
@admin_only()
async def admin_list_produtos(interaction: discord.Interaction):
    if not products:
        await interaction.response.send_message("Não há produtos.", ephemeral=True)
        return
    desc = []
    for sku, data in products.items():
        p = Produto.from_dict(sku, data)
        desc.append(f"• **{p.nome}** (`{p.sku}`) — {moeda()} {p.preco:,.2f} | Estoque: {len(p.stock)}")
    embed = criar_embed(title="📦 Produtos (Admin)", description="\n".join(desc), color=cor_embed())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="definir_pix", description="Define a chave PIX do painel")
@admin_only()
@app_commands.describe(chave="Chave PIX")
async def admin_set_pix(interaction: discord.Interaction, chave: str):
    persisted_config["pix_key"] = chave
    save_json(CONFIG_FILE, persisted_config)
    await interaction.response.send_message("✅ Chave PIX atualizada.", ephemeral=True)

@tree.command(name="definir_cargo_staff", description="Define o nome do cargo de staff")
@admin_only()
@app_commands.describe(cargo="Nome exato do cargo")
async def admin_set_staff(interaction: discord.Interaction, cargo: str):
    persisted_config["cargo_staff"] = cargo
    save_json(CONFIG_FILE, persisted_config)
    await interaction.response.send_message(f"✅ Cargo de staff atualizado para **{cargo}**.", ephemeral=True)

@tree.command(name="definir_categoria_ticket", description="Define/Cria a categoria de tickets")
@admin_only()
@app_commands.describe(nome="Nome da categoria")
async def admin_set_categoria(interaction: discord.Interaction, nome: str):
    persisted_config["categoria_tickets"] = nome
    save_json(CONFIG_FILE, persisted_config)
    cat = await ensure_tickets_category(interaction.guild)
    if cat:
        await interaction.response.send_message(f"✅ Categoria definida: **{cat.name}**.", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ Não consegui criar a categoria (permissões?).", ephemeral=True)

@tree.command(name="ajuda_vendas", description="Lista comandos e suas funções")
async def ajuda_cmd(interaction: discord.Interaction):
    txt = (
        "**Comandos disponíveis:**\n"
        "• `/criar_produto` — Adiciona ou atualiza um produto\n"
        "• `/adicionar_estoque` — Adiciona código(s) ao estoque de um produto\n"
        "• `/postar_painel` — Cria um painel de venda de um produto\n"
        "• `/aprovar` — Aprova ticket e envia código por DM\n"
        "• `/recusar` — Recusa ticket\n"
        "• `/atualizar_preco` — Atualiza o preço de um produto\n"
        "• `/listar_produtos_admin` — Lista todos os produtos detalhado (staff)\n"
        "• `/definir_pix` — Define a chave PIX do painel\n"
        "• `/definir_cargo_staff` — Define o cargo de staff\n"
        "• `/definir_categoria_ticket` — Define/Cria categoria de tickets\n"
        "• `/produtos` — Lista produtos disponíveis para clientes\n"
        "• `/remover_produto` — Deleta um produto pelo SKU\n"
        "• `/admin_add_varios_produtos` — Adiciona vários produtos de uma vez"
    )
    await interaction.response.send_message(txt, ephemeral=True)


@tree.command(name="aprovar", description="Aprova ticket e envia 1 código por DM")
@admin_only()
async def aprovar_cmd(interaction: discord.Interaction):
    ch = interaction.channel
    if not isinstance(ch, discord.TextChannel):
        await interaction.response.send_message("Use isso dentro do canal do ticket.", ephemeral=True)
        return

    info = active_tickets.get(ch.id)
    if not info and ch.topic and "SKU=" in ch.topic and "Ticket de " in ch.topic:
        try:
            uid = int(ch.topic.split("Ticket de ")[1].split(" | ")[0])
            sku = ch.topic.split("SKU=")[1].strip()
            info = {"user_id": uid, "sku": sku}
            active_tickets[ch.id] = info
        except:
            pass

    if not info:
        await interaction.response.send_message("❌ Não consegui identificar o ticket.", ephemeral=True)
        return

    user = interaction.guild.get_member(info["user_id"])
    sku = str(info["sku"])
    produto = get_produto(sku)
    if not produto:
        await interaction.response.send_message("❌ Produto não encontrado.", ephemeral=True)
        return

    if not produto.stock:
        await interaction.response.send_message(f"⚠️ Estoque esgotado para `{produto.sku}`.", ephemeral=True)
        return

    codigo_entregue = produto.stock.pop(0)
    set_produto(produto)

    embed_dm = criar_embed(
        title=f"✅ Sua compra foi aprovada — {produto.nome}",
        description=f"**Produto:** {produto.nome}\n**Preço** {moeda()} {produto.preco:,.2f}",
        color=0x57F287
    )
    if banner_url():
        embed_dm.set_thumbnail(url=banner_url())

    await send_dm_safe(user, embed_dm)
    await enviar_feedback_embed(user, produto, codigo_entregue)
    await interaction.response.send_message("✅ Aprovado e código enviado (ou tentado) por DM.", ephemeral=True)
    active_tickets.pop(ch.id, None)
    try:
        await ch.delete(reason="Ticket finalizado (aprovado)")
    except:
        await ch.send("⚠️ Não consegui apagar o canal (permissões?).")

@tree.command(name="remover_produto", description="Deleta um produto pelo SKU")
@admin_only()
@app_commands.describe(sku="SKU do produto a ser deletado")
async def admin_del_produto(interaction: discord.Interaction, sku: str):
    sku = sku.upper()
    if sku not in products:
        await interaction.response.send_message("❌ Produto não encontrado.", ephemeral=True)
        return
    products.pop(sku)
    save_json(PRODUCTS_FILE, products)
    await interaction.response.send_message(f"✅ Produto `{sku}` deletado com sucesso.", ephemeral=True)

@tree.command(name="admin_add_varios_produtos", description="Adiciona vários produtos de uma vez")
@admin_only()
@app_commands.describe(lista_produtos="Lista de produtos separados por linha: SKU,Nome,Preço,Descrição")
async def admin_add_varios_produtos(interaction: discord.Interaction, lista_produtos: str):
    linhas = [l.strip() for l in lista_produtos.splitlines() if l.strip()]
    adicionados = 0
    for linha in linhas:
        try:
            sku, nome, preco, descricao = [x.strip() for x in linha.split(",", 3)]
            preco = float(preco)
            p = Produto(sku.upper(), nome, preco, descricao, stock=[])
            set_produto(p)
            bot.add_view(ComprarView(p.sku))
            adicionados += 1
        except Exception as e:
            await interaction.followup.send(f"⚠️ Erro ao adicionar linha: `{linha}` | {e}", ephemeral=True)
    await interaction.response.send_message(f"✅ {adicionados} produto(s) adicionados.", ephemeral=True)

@tree.command(name="recusar", description="Recusa ticket")
@admin_only()
@app_commands.describe(motivo="Motivo opcional")
async def recusar_cmd(interaction: discord.Interaction, motivo: Optional[str] = None):
    ch = interaction.channel
    if not isinstance(ch, discord.TextChannel):
        await interaction.response.send_message("Use isso dentro do canal do ticket.", ephemeral=True)
        return

    info = active_tickets.get(ch.id)
    user = interaction.guild.get_member(info["user_id"]) if info else None
    texto = "❌ Seu pedido foi **recusado**."
    if motivo:
        texto += f"\n**Motivo:** {motivo}"

    if user:
        embed_dm = criar_embed(title="❌ Pedido recusado", description=texto, color=0xED4245)
        await send_dm_safe(user, embed_dm)

    await interaction.response.send_message("✅ Ticket recusado.", ephemeral=True)
    active_tickets.pop(ch.id, None)
    try:
        await ch.delete(reason="Ticket finalizado (recusado)")
    except:
        await ch.send("⚠️ Não consegui apagar o canal (permissões?).")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)

