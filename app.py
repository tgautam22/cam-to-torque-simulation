# Streamlit page for cam-to-torque. Run with:  streamlit run app.py
import streamlit as st

from calc import Params, run
from plots import animated_fig

st.set_page_config(page_title="cam-to-torque", layout="wide")

# ---------- inputs ----------
d = Params() # defaults
sb = st.sidebar
sb.header("Cam shape")
Rb = sb.number_input("Base radius R_b (mm)", value=d.Rb, step=1.0)
h = sb.number_input("Max lift h (mm)", value=d.h, step=1.0)
rise_start = sb.number_input("Rise start (deg)", value=d.rise_start, step=5.0)
rise = sb.number_input("Rise angle (deg)", value=d.rise, step=5.0)
dwell = sb.number_input("Top dwell (deg)", value=d.dwell, step=5.0)
fall = sb.number_input("Fall angle (deg)", value=d.fall, step=5.0)
sb.header("Follower and spring")
Rf = sb.number_input("Roller radius R_f (mm)", value=d.Rf, step=0.5)
off = sb.number_input("Offset d (mm)", value=d.d, step=0.5)
k = sb.number_input("Spring k (N/mm)", value=d.k, step=5.0)
s0 = sb.number_input("Preload s0 (mm)", value=d.s0, step=0.5)

p = Params(Rb, h, rise_start, rise, dwell, fall, Rf, off, k, s0)
error = p.check()
if error:
    st.error(error)
    st.stop() # nothing below runs until the inputs are fixed


@st.cache_data # only rebuilds when an input changes
def build(p):
    return animated_fig(run(p), p)


fig = build(p)

# ---------- page ----------
tab_mech, tab_method = st.tabs(["Mechanism", "Method"])

with tab_mech:
    st.plotly_chart(fig, width="stretch") # Play, Pause and the angle slider are inside the figure; it animates in the browser

with tab_method:
    st.markdown("**1. Bump** (cycloidal rise, x = (φ − rise start) / rise angle)")
    st.latex(r"L(\varphi) = h\left(x - \frac{\sin 2\pi x}{2\pi}\right) \;\rightarrow\; h \text{ on the dwell} \;\rightarrow\; \text{reversed on the fall} \;\rightarrow\; 0")
    st.markdown("**2. Cam shape** (every 0.1°)")
    st.latex(r"R(\varphi) = R_b + L(\varphi)")
    st.markdown("**3. Turn the cam to θ:** where cam point φ sits")
    st.latex(r"x = R\sin(\varphi - \theta), \qquad y_{point} = R\cos(\varphi - \theta)")
    st.markdown("**4. Roller centre if it touched that point** (follower line at x = d, only points with |x − d| ≤ R_f)")
    st.latex(r"y_{roller}(\varphi) = y_{point} + \sqrt{R_f^2 - (x - d)^2}")
    st.markdown("**5. Actual roller centre:** the point it really touches")
    st.latex(r"y_{roller}(\theta) = \max_{\varphi}\, y_{roller}(\varphi)")
    st.markdown("**6. Lift**")
    st.latex(r"\text{lift}(\theta) = y_{roller}(\theta) - \sqrt{(R_b + R_f)^2 - d^2}")
    st.markdown("**7. Spring compression**")
    st.latex(r"s(\theta) = s_0 + \text{lift}(\theta)")
    st.markdown("**8. Slope**")
    st.latex(r"\frac{ds}{d\theta} = \frac{s(\theta + 0.1^\circ) - s(\theta - 0.1^\circ)}{0.2^\circ \text{ in radians}}")
    st.markdown("**9. Torque** (Realmuto Eq. 23 reversed)")
    st.latex(r"T(\theta) = k \, s \, \frac{ds}{d\theta}")