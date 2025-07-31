# 🤝 Guia de Contribuição - FinBot

Obrigado por considerar contribuir com o FinBot! Este documento fornece diretrizes para contribuições.

## 🚀 Como Contribuir

### **1. Fork e Clone**
```bash
# Fork o repositório no GitHub
# Clone seu fork
git clone https://github.com/seu-usuario/finbot_project.git
cd finbot_project

# Adicione o repositório original como upstream
git remote add upstream https://github.com/original/finbot_project.git
```

### **2. Configure o Ambiente**
```bash
# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Configure o ambiente
cp env.template .env
# Edite .env com suas configurações
```

### **3. Crie uma Branch**
```bash
# Atualize sua branch principal
git checkout main
git pull upstream main

# Crie uma branch para sua feature
git checkout -b feature/sua-feature
```

### **4. Desenvolva**
- ✅ Siga as convenções de código
- ✅ Escreva testes para novas funcionalidades
- ✅ Atualize documentação quando necessário
- ✅ Execute testes antes de commitar

### **5. Commit e Push**
```bash
# Adicione suas mudanças
git add .

# Commit com mensagem descritiva
git commit -m "feat: adiciona nova funcionalidade de análise"

# Push para sua branch
git push origin feature/sua-feature
```

### **6. Pull Request**
- Crie um Pull Request no GitHub
- Descreva suas mudanças detalhadamente
- Inclua testes e documentação
- Aguarde review da equipe

## 📋 Convenções de Código

### **Estilo Python**
- ✅ Siga PEP 8
- ✅ Use type hints
- ✅ Documente funções e classes
- ✅ Mantenha linhas com máximo 88 caracteres

### **Mensagens de Commit**
Use o formato Conventional Commits:
```
feat: adiciona nova funcionalidade
fix: corrige bug na validação
docs: atualiza documentação
test: adiciona testes para feature
refactor: refatora código existente
style: formata código
perf: melhora performance
```

### **Estrutura de Arquivos**
```
app/
├── backend.py          # Lógica principal
├── config.py           # Configurações
├── paginas/            # Páginas da UI
└── componentes/        # Componentes reutilizáveis

tests/
├── test_backend.py     # Testes do backend
└── test_ui.py         # Testes da interface

docs/
├── API.md             # Documentação da API
└── DEPLOYMENT.md      # Guia de deploy
```

## 🧪 Testes

### **Executar Testes**
```bash
# Todos os testes
python run_tests.py

# Testes específicos
pytest tests/test_backend.py -v

# Com cobertura
pytest --cov=app tests/
```

### **Escrever Testes**
```python
def test_nova_funcionalidade():
    """Testa nova funcionalidade."""
    # Arrange
    dados = criar_dados_teste()
    
    # Act
    resultado = processar_dados(dados)
    
    # Assert
    assert resultado is not None
    assert len(resultado) > 0
```

## 📝 Documentação

### **Atualizar Documentação**
- ✅ Atualize README.md para mudanças significativas
- ✅ Documente novas APIs em API.md
- ✅ Atualize CHANGELOG.md
- ✅ Adicione exemplos de uso

### **Padrões de Documentação**
```python
def nova_funcao(param1: str, param2: int) -> dict:
    """
    Descrição da função.
    
    Args:
        param1: Descrição do primeiro parâmetro
        param2: Descrição do segundo parâmetro
        
    Returns:
        dict: Descrição do retorno
        
    Raises:
        ValueError: Quando parâmetros são inválidos
        
    Example:
        >>> resultado = nova_funcao("teste", 42)
        >>> print(resultado)
        {'status': 'success'}
    """
    pass
```

## 🔍 Code Review

### **Checklist para Review**
- ✅ Código segue convenções
- ✅ Testes passam
- ✅ Documentação atualizada
- ✅ Performance considerada
- ✅ Segurança verificada
- ✅ Acessibilidade mantida

### **Comentários de Review**
- Seja construtivo e respeitoso
- Explique o "porquê" das sugestões
- Reconheça boas práticas
- Sugira alternativas quando apropriado

## 🚀 Deploy e Release

### **Processo de Release**
1. **Desenvolva** em branch feature
2. **Teste** completamente
3. **Merge** para main
4. **Tag** versão (v2.1.0)
5. **Deploy** automático
6. **Anuncie** mudanças

### **Versionamento**
- **MAJOR**: Mudanças incompatíveis
- **MINOR**: Novas funcionalidades
- **PATCH**: Correções de bugs

## 🆘 Precisando de Ajuda?

### **Canais de Suporte**
- 📧 Email: [support@finbot-project.com](mailto:support@finbot-project.com)
- 💬 Discord: [Link do servidor](https://discord.gg/finbot)
- 📖 Wiki: [Documentação completa](https://github.com/finbot/wiki)

### **Recursos Úteis**
- 🛠️ [Guia de Desenvolvimento](DEVELOPMENT.md)
- 🧪 [Guia de Testes](TESTING.md)
- 🚀 [Guia de Deploy](DEPLOYMENT.md)

## 🎉 Reconhecimento

Contribuições são reconhecidas de várias formas:
- ✅ Menção no README.md
- ✅ Badge de contribuidor
- ✅ Acesso a recursos premium
- ✅ Participação em decisões do projeto

---

**Obrigado por contribuir com o FinBot! 🤖💰** 