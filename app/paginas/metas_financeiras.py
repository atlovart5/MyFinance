import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# --- DADOS DAS TAREFAS ---
# Aqui você pode adicionar, remover ou editar suas tarefas.
# As pontuações devem ser de 1 a 5.
tasks = [
    {
        "name": "Trocar lixeiras de tinta por papelão",
        "impact_scores": {"waste": 4, "productivity": 3, "organization": 5, "cost": 4},
        "effort_scores": {"cost": 1, "time": 1, "complexity": 2},
    },
    {
        "name": "Organizar o porta-clichês",
        "impact_scores": {"waste": 3, "productivity": 3, "organization": 5, "cost": 3},
        "effort_scores": {"cost": 1, "time": 2, "complexity": 2},
    },
    {
        "name": "Mudar o layout da produção",
        "impact_scores": {"waste": 5, "productivity": 5, "organization": 4, "cost": 4},
        "effort_scores": {"cost": 4, "time": 5, "complexity": 5},
    },
    {
        "name": "Fazer armário novo",
        "impact_scores": {"waste": 3, "productivity": 3, "organization": 5, "cost": 3},
        "effort_scores": {"cost": 4, "time": 4, "complexity": 3},
    },
    {
        "name": "Criar área de recebimento",
        "impact_scores": {"waste": 4, "productivity": 4, "organization": 5, "cost": 3},
        "effort_scores": {"cost": 4, "time": 5, "complexity": 3},
    },
    {
        "name": "Padronizar processo de setup",
        "impact_scores": {"waste": 5, "productivity": 5, "organization": 4, "cost": 4},
        "effort_scores": {"cost": 2, "time": 4, "complexity": 3},
    },
]

# --- PESOS PARA OS CÁLCULOS ---
# Estes são os pesos que definimos anteriormente.
IMPACT_WEIGHTS = {"waste": 0.35, "productivity": 0.35, "organization": 0.20, "cost": 0.10}
EFFORT_WEIGHTS = {"cost": 0.40, "time": 0.35, "complexity": 0.25}

def calculate_weighted_score(scores, weights):
    """Calcula a pontuação ponderada para impacto ou esforço."""
    total_score = 0
    for key in scores:
        total_score += scores[key] * weights[key]
    return total_score

def get_quadrant(impact_score, effort_score):
    """Determina o quadrante com base nas pontuações de impacto e esforço."""
    if impact_score >= 3 and effort_score < 3:
        return "1. Ataque Rápido (Quick Win)"
    elif impact_score >= 3 and effort_score >= 3:
        return "2. Grandes Projetos"
    elif impact_score < 3 and effort_score < 3:
        return "3. Tarefas de Preenchimento"
    else: # impact_score < 3 and effort_score >= 3
        return "4. Considerar Descartar"

def analyze_tasks(task_list):
    """Processa a lista de tarefas, calcula as pontuações e determina o quadrante."""
    results = []
    for task in task_list:
        impact_score = calculate_weighted_score(task["impact_scores"], IMPACT_WEIGHTS)
        effort_score = calculate_weighted_score(task["effort_scores"], EFFORT_WEIGHTS)
        quadrant = get_quadrant(impact_score, effort_score)
        
        results.append({
            "name": task["name"],
            "impact": impact_score,
            "effort": effort_score,
            "quadrant": quadrant
        })
    return results

def plot_matrix(results):
    """Cria e exibe um gráfico de dispersão da matriz de Esforço x Impacto."""
    fig, ax = plt.subplots(figsize=(10, 8))

    # Define cores para cada quadrante para uma melhor visualização
    color_map = {
        "1. Ataque Rápido (Quick Win)": 'green',
        "2. Grandes Projetos": 'blue',
        "3. Tarefas de Preenchimento": 'orange',
        "4. Considerar Descartar": 'red'
    }

    # Adiciona os pontos de dados ao gráfico
    for item in results:
        ax.scatter(
            item['effort'], 
            item['impact'], 
            color=color_map[item['quadrant']],
            s=100,  # Tamanho do ponto
            alpha=0.7,
            label=item['quadrant'] # Adiciona a legenda
        )
        # Adiciona o nome da tarefa perto do ponto
        ax.text(item['effort'] + 0.05, item['impact'] + 0.05, item['name'], fontsize=9)

    # Desenha as linhas que dividem os quadrantes
    ax.axhline(y=3, color='grey', linestyle='--', linewidth=1.5)
    ax.axvline(x=3, color='grey', linestyle='--', linewidth=1.5)

    # Configurações do gráfico
    ax.set_title('Matriz de Esforço x Impacto', fontsize=16, fontweight='bold')
    ax.set_xlabel('Esforço Total', fontsize=12)
    ax.set_ylabel('Impacto Total', fontsize=12)
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 5)
    ax.grid(True, which='both', linestyle=':', linewidth=0.5)

    # Adiciona os nomes dos quadrantes no gráfico
    ax.text(1.5, 4.0, 'Ataques Rápidos', fontsize=12, ha='center', alpha=0.6)
    ax.text(4.0, 4.0, 'Grandes Projetos', fontsize=12, ha='center', alpha=0.6)
    ax.text(1.5, 1.0, 'Tarefas de Preenchimento', fontsize=12, ha='center', alpha=0.6)
    ax.text(4.0, 1.0, 'Considerar Descartar', fontsize=12, ha='center', alpha=0.6)
    
    # Cria uma legenda sem duplicatas
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), title='Quadrantes')

    plt.show()


def main():
    """Função principal que executa o programa."""
    # 1. Analisa as tarefas
    analysis_results = analyze_tasks(tasks)
    
    # 2. Imprime os resultados no console
    print("--- Análise de Priorização de Tarefas ---")
    for item in sorted(analysis_results, key=lambda x: x['quadrant']):
        print(f"\nTarefa: {item['name']}")
        print(f"  - Impacto Total: {item['impact']:.2f}")
        print(f"  - Esforço Total: {item['effort']:.2f}")
        print(f"  - Quadrante: {item['quadrant']}")
    print("\n--- Fim da Análise ---")
    
    # 3. Gera o gráfico visual
    print("\nA gerar o gráfico da matriz...")
    plot_matrix(analysis_results)

def layout():
    """
    Renderiza o conteúdo da página de Metas Financeiras.
    """
    st.subheader("Metas Financeiras")
    st.write("Configure e acompanhe suas metas financeiras aqui.")
    
    # Placeholder para funcionalidade futura
    st.info("Funcionalidade em desenvolvimento. Em breve você poderá configurar e acompanhar suas metas financeiras.")

# Executa a função principal quando o script é chamado
if __name__ == "__main__":
    main()
