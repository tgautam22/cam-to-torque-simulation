# Figures for cam-to-torque: one animated figure with the mechanism, lift graph and torque graph.
# Nothing is calculated here except turning points for drawing; all values come from calc.run().
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from calc import STEP

BG = "#0E1117" # matches the dark page background
CAM_FILL = "#2B3542"
LINE = "#C7D0D9"
PART = "#8FB3D9"
SPRING = "#E0A84F"
ACCENT = "#5B8DEF"
LIFT_COL = "#A78BFA"
TORQUE_COL = "#4FB3E8"
GRID = "#252C38"
TEXT = "#E6EDF3"
ANGLE_LINE = "#5A6573"

FRAME_STEP = 2 # deg between animation frames
CAM_EVERY = 5 # draw every 5th outline point (0.5 deg) to keep the animation light


def _index(theta): # position of an angle in the 0.1 deg arrays
    return int(round((theta % 360) / STEP))


def _circle(cx, cy, r, n=90): # points around a circle, for drawing
    t = np.linspace(0, 2 * np.pi, n)
    return (cx + r * np.cos(t)).round(2), (cy + r * np.sin(t)).round(2)


def _sizes(p): # fixed drawing sizes
    span = p.Rb + p.h + 6 # half-width of the drawing area
    base = np.sqrt((p.Rb + p.Rf) ** 2 - p.d**2) # roller centre height on the base circle
    top = base + p.h + 2.4 * p.Rf + 0.9 * (p.Rb + p.h) # fixed plate the spring pushes against (when alpha = 0)
    sw = max(0.9 * p.Rf, 5) # spring half-width
    return span, base, top, sw


def _axis(p): # spring axis at angle alpha from vertical, starting at the roller's rest centre
    a = np.radians(p.alpha)
    u = np.array([np.sin(a), np.cos(a)]) # along the spring
    n = np.array([-np.cos(a), np.sin(a)]) # across the spring (the side the rod tip slides to)
    o = np.array([p.d, _sizes(p)[1]]) # roller centre at rest
    return o, u, n


def _frame(r, p, theta): # every part that is redrawn each frame, in drawing order (later = on top)
    span, base, top, sw = _sizes(p)
    i = _index(theta)
    c, s = np.cos(np.radians(theta)), np.sin(np.radians(theta))
    x0, y0 = np.append(r.x0[::CAM_EVERY], r.x0[0]), np.append(r.y0[::CAM_EVERY], r.y0[0]) # closed outline
    cam_x = (x0 * c - y0 * s).round(2) # cam outline turned by theta
    cam_y = (x0 * s + y0 * c).round(2)
    yc = r.y_roller[i] # roller centre height from calc
    o, u, n = _axis(p)
    rod = 2.2 * p.Rf # rod length, fixed to the roller at angle alpha
    tip = np.array([p.d, yc]) + rod * u # rod tip: rises straight up with the roller
    M = o + (rod + r.s[i] - p.s0) * u # spring's moving end: pushed along the axis by lift*cos(alpha)
    A = o + (top - base) * u # spring's fixed end
    zig = [sw if k % 2 else -sw for k in range(1, 20)] # spring zigzag offsets
    t = np.linspace(0, 1, 21)[1:-1]
    zx = np.round([M[0]] + [M[0] + (A[0] - M[0]) * tk + n[0] * z for tk, z in zip(t, zig)] + [A[0]], 2)
    zy = np.round([M[1]] + [M[1] + (A[1] - M[1]) * tk + n[1] * z for tk, z in zip(t, zig)] + [A[1]], 2)
    reach = max(1.3 * sw, r.lift.max() * u[0] + 0.6 * sw) # plate wide enough for the rod tip to slide lift*sin(alpha) across
    seat = [M - 1.3 * sw * n, M + reach * n] # spring's moving end plate
    bx, by = _circle(0, 0, p.Rb, 180)
    rx, ry = _circle(p.d, yc, p.Rf)
    lx = p.d + p.Rf + 4 # lift dimension x position
    text = (f"<b>θ = {theta:.0f}°</b><br>Lift  {r.lift[i]:.2f} mm<br>"
            f"Compression  {r.s[i]:.2f} mm<br>Torque  {r.T[i]:.2f} N·m")
    return [
        go.Scatter(x=cam_x, y=cam_y), # cam
        go.Scatter(x=bx, y=by), # base circle
        go.Scatter(x=[p.d, p.d], y=[-span, top]), # follower line
        go.Scatter(x=[0], y=[0]), # cam centre O
        go.Scatter(x=[0, -0.7 * p.Rb * s], y=[0, 0.7 * p.Rb * c]), # cam's 0 deg mark
        go.Scatter(x=zx, y=zy), # spring
        go.Scatter(x=[p.d, tip[0]], y=[yc, tip[1]]), # rod
        go.Scatter(x=[seat[0][0], seat[1][0]], y=[seat[0][1], seat[1][1]]), # spring's moving end plate
        go.Scatter(x=rx, y=ry), # roller
        go.Scatter(x=[p.d], y=[yc]), # roller centre
        go.Scatter(x=[lx, lx], y=[base, yc]), # lift dimension
        go.Scatter(x=[p.d - 2 * sw], y=[top - 2], text=[text]), # readout: right edge just left of the spring, grows to the left
        go.Scatter(x=[theta], y=[r.lift[i]]), # dot on lift graph
        go.Scatter(x=[theta, theta], y=[min(r.lift.min(), 0), r.lift.max()]), # angle line on lift graph
        go.Scatter(x=[theta], y=[r.T[i]]), # dot on torque graph
        go.Scatter(x=[theta, theta], y=[r.T.min(), r.T.max()]), # angle line on torque graph
    ]


STYLE = [ # look of each part in _frame, same order; set once, frames only change x, y and text
    dict(mode="lines", fill="toself", fillcolor=CAM_FILL, line=dict(color=LINE, width=2.5)), # cam
    dict(mode="lines", line=dict(color=LINE, width=1, dash="dot")), # base circle
    dict(mode="lines", line=dict(color=LINE, width=1, dash="dashdot")), # follower line
    dict(mode="markers+text", text=["O"], textposition="bottom left", marker=dict(color=LINE, size=7)), # cam centre O
    dict(mode="lines", line=dict(color=ACCENT, width=3)), # 0 deg mark
    dict(mode="lines", line=dict(color=SPRING, width=2.5)), # spring
    dict(mode="lines", line=dict(color=PART, width=6)), # rod
    dict(mode="lines", line=dict(color=PART, width=4)), # seat
    dict(mode="lines", fill="toself", fillcolor=BG, line=dict(color=PART, width=2.5)), # roller
    dict(mode="markers", marker=dict(color=PART, size=6)), # roller centre
    dict(mode="lines+markers", line=dict(color=ACCENT, width=1.5),
         marker=dict(symbol="line-ew", size=10, line=dict(width=2, color=ACCENT))), # lift dimension
    dict(mode="text", textposition="bottom left", cliponaxis=False, textfont=dict(size=15, color=TEXT)), # readout
    dict(mode="markers", marker=dict(color=LIFT_COL, size=12, line=dict(color=BG, width=2))), # lift dot
    dict(mode="lines", line=dict(color=ANGLE_LINE, width=1)), # lift angle line
    dict(mode="markers", marker=dict(color=TORQUE_COL, size=12, line=dict(color=BG, width=2))), # torque dot
    dict(mode="lines", line=dict(color=ANGLE_LINE, width=1)), # torque angle line
]
WHERE = [(1, 1)] * 12 + [(1, 2)] * 2 + [(2, 2)] * 2 # subplot of each part: drawing, lift graph, torque graph


def animated_fig(r, p):
    span, base, top, sw = _sizes(p)
    skip = dict(hoverinfo="skip", showlegend=False)
    fig = make_subplots(rows=2, cols=2, column_widths=[0.45, 0.55], horizontal_spacing=0.09, vertical_spacing=0.16,
                        specs=[[{"rowspan": 2}, {}], [None, {}]],
                        subplot_titles=("Mechanism", "Lift", "Torque"))

    for tr, st, (row, col) in zip(_frame(r, p, 0), STYLE, WHERE): # parts redrawn every frame
        fig.add_trace(tr.update(**st, **skip), row, col)
    moving = list(range(len(fig.data))) # indices the frames update

    o, u, n = _axis(p)
    A = o + (top - base) * u # spring's fixed end
    fig.add_trace(go.Scatter(x=[A[0] - 1.6 * sw * n[0], A[0] + 1.6 * sw * n[0]], y=[A[1] - 1.6 * sw * n[1], A[1] + 1.6 * sw * n[1]], mode="lines",
                             line=dict(color=LINE, width=5), **skip), 1, 1) # fixed plate
    fig.add_trace(go.Scatter(x=r.theta, y=r.lift, mode="lines", line=dict(color=LIFT_COL, width=3.5), fill="tozeroy", fillcolor="rgba(167,139,250,0.12)", showlegend=False,
                             hovertemplate="θ %{x:.1f}°<br>lift %{y:.2f} mm<extra></extra>"), 1, 2) # lift curve
    fig.add_trace(go.Scatter(x=r.theta, y=r.T, mode="lines", line=dict(color=TORQUE_COL, width=3.5), fill="tozeroy", fillcolor="rgba(79,179,232,0.12)", showlegend=False,
                             hovertemplate="θ %{x:.1f}°<br>torque %{y:.2f} N·m<extra></extra>"), 2, 2) # torque curve

    angles = np.arange(0, 360, FRAME_STEP)
    fig.frames = [go.Frame(name=f"{a:g}", data=_frame(r, p, a), traces=moving) for a in angles] # sent to the browser once

    play = dict(frame=dict(duration=40, redraw=True), transition=dict(duration=0), fromcurrent=True, mode="immediate")
    pause = dict(frame=dict(duration=0, redraw=False), mode="immediate")
    fig.update_layout(
        height=760, margin=dict(l=10, r=20, t=40, b=90), plot_bgcolor=BG, paper_bgcolor=BG,
        font=dict(size=14, color=TEXT), hoverlabel=dict(font_size=13, bgcolor="#171C26", font_color=TEXT),
        updatemenus=[dict(type="buttons", direction="left", x=0, y=-0.08, xanchor="left", yanchor="top", showactive=False, # no white highlight on the pressed button
                          bgcolor="#171C26", bordercolor="#3A4452", font=dict(size=14, color=TEXT),
                          buttons=[dict(label="Play", method="animate", args=[None, play]),
                                   dict(label="Pause", method="animate", args=[[None], pause])])],
        sliders=[dict(x=0.18, y=-0.08, len=0.82, xanchor="left", yanchor="top", pad=dict(t=0),
                      bgcolor="#2B3542", activebgcolor=ACCENT, bordercolor="#3A4452",
                      ticklen=0, font=dict(color="rgba(0,0,0,0)"), # hide the 180 step labels
                      currentvalue=dict(prefix="Cam angle θ = ", suffix="°", font=dict(size=14, color=TEXT)),
                      steps=[dict(label=f"{a:g}", method="animate",
                                  args=[[f"{a:g}"], dict(frame=dict(duration=0, redraw=True), mode="immediate")])
                             for a in angles])],
    )
    right = max(span + abs(p.d) + 20, A[0] + 2 * sw + 4) # room for a tilted spring
    fig.update_xaxes(visible=False, range=[-span - 30, right], row=1, col=1) # extra room on the left for the readout
    fig.update_yaxes(visible=False, range=[-span, top + 4], scaleanchor="x", scaleratio=1, row=1, col=1) # circles stay round
    for row, title in [(1, "lift (mm)"), (2, "torque (N·m)")]:
        fig.update_xaxes(range=[0, 360], dtick=60, gridcolor=GRID, showline=True, linecolor="#3A4452",
                         tickfont=dict(size=13, color=TEXT), row=row, col=2)
        fig.update_yaxes(title=title, gridcolor=GRID, zerolinecolor="#6B7684", zerolinewidth=1.5, showline=True,
                         linecolor="#3A4452", tickfont=dict(size=13, color=TEXT), row=row, col=2)
    fig.update_xaxes(title="cam angle θ (deg)", row=2, col=2)
    fig.update_annotations(font=dict(size=16, color=TEXT)) # subplot titles
    return fig