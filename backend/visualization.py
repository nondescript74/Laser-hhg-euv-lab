import plotly.graph_objects as go
from plotly.subplots import make_subplots

STAGE_CONFIG = [
    ("aerial_image", "Aerial Image (Target Pattern)", "Viridis"),
    ("acid_map", "Acid Map (Post-Exposure)", "Hot"),
    ("deprotection", "Deprotection Profile (Post-PEB)", "Plasma"),
    ("dissolution_rate", "Dissolution Rate (Mack Model)", "Inferno"),
]


def build_pipeline_figure(stages, title="EUV Lithography Simulation Pipeline"):
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[cfg[1] for cfg in STAGE_CONFIG],
        horizontal_spacing=0.08,
        vertical_spacing=0.12,
    )

    for idx, (key, label, colorscale) in enumerate(STAGE_CONFIG):
        row, col = divmod(idx, 2)
        fig.add_trace(
            go.Heatmap(
                z=stages[key],
                colorscale=colorscale,
                colorbar=dict(len=0.4, y=0.78 - row * 0.56, x=0.47 + col * 0.53),
                hovertemplate="x: %{x}<br>y: %{y}<br>value: %{z:.4f}<extra></extra>",
            ),
            row=row + 1, col=col + 1,
        )

    fig.update_layout(
        title_text=title,
        height=900,
        width=1000,
    )
    return fig
