import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Dados iniciais
df = pd.DataFrame([
    {"id": 1, "nome": "Carlos", "escola": "Recife"},
    {"id": 2, "nome": "Ana", "escola": "Olinda"},
])

# Configura o grid com seleção
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection("single", use_checkbox=True)
grid_options = gb.build()

# Renderiza o grid
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    theme="streamlit"
)

# Captura a linha selecionada
linha = grid_response["selected_rows"]

if linha:
    selecionado = linha[0]
    st.subheader("✏️ Formulário de edição")

    # Campos de edição
    novo_nome = st.text_input("Nome", value=selecionado["nome"], key=f"nome_{selecionado['id']}")
    nova_escola = st.selectbox(
        "Escola",
        options=["Recife", "Olinda", "Jaboatão"],
        index=["Recife", "Olinda", "Jaboatão"].index(selecionado["escola"]),
        key=f"escola_{selecionado['id']}"
    )

    # Botão de salvar
    if st.button("💾 Salvar alterações"):
        # Atualiza os dados no DataFrame
        df.loc[df["id"] == selecionado["id"], "nome"] = novo_nome
        df.loc[df["id"] == selecionado["id"], "escola"] = nova_escola
        st.success("Dados atualizados com sucesso!")

        # Reexibe o grid com dados atualizados
        AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            theme="streamlit"
        )