import streamlit as st
import traceback

try:
    errors = []

    try:  
      from sympy import Symbol, Eq
    except Exception as e:
      errors.append(e)

    try:
      import modulus.sym
    except Exception as e:
      errors.append(e)


    try:
      from modulus.sym.hydra import instantiate_arch, ModulusConfig
    except Exception as e:
      errors.append(e)


    try:
      from modulus.sym.solver import Solver
    except Exception as e:
      errors.append(e)

    try:
      from modulus.sym.domain import Domain
    except Exception as e:
      errors.append(e)

    try:
      from modulus.sym.geometry.primitives_2d import Rectangle, Circle
    except Exception as e:
      errors.append(e)

    try:
      from modulus.sym.domain.constraint import (
      PointwiseBoundaryConstraint,
      PointwiseInteriorConstraint,
      )
    except Exception as e:
      errors.append(e)

    try:
      from modulus.sym.domain.validator import PointwiseValidator
    except Exception as e:
      errors.append(e)

    try:
      from modulus.sym.domain.inferencer import PointwiseInferencer
    except Exception as e:
      errors.append(e)

    try:
      from modulus.sym.utils.io import InferencerPlotter
    except Exception as e:
      errors.append(e)

    try:
      from modulus.sym.key import Key
    except Exception as e:
      errors.append(e)

    try:
      from modulus.sym.node import Node
    except Exception as e:
      errors.append(e)

    try:
      from modulus.sym.eq.pdes.linear_elasticity import LinearElasticityPlaneStress
    except Exception as e:
      errors.append(e)

    try:
      from modulus.sym.eq.pdes.linear_elasticity import LinearElasticity
    except Exception as e:
      errors.append(e)

    try:
      from modulus.sym.hydra.utils import compose
    except Exception as e:
      errors.append(e)

    try:
      from modulus.sym.hydra import to_yaml
    except Exception as e:
      errors.append(e)

    try:
      cfg = compose(config_path="conf", config_name="config")
    except Exception as e:
      errors.append(e)

      # print(to_yaml(cfg))
    try:
      import matplotlib.pyplot as plt
    except Exception as e:
      errors.append(e)

    try:
      from PIL import Image
    except Exception as e:
      errors.append(e)

    try:
      from io import BytesIO
    except Exception as e:
      errors.append(e)

    print(errors)
    if errors:
        st.write([' '.join(str(x) for x in errors)])

    # ---------- Start of Streamlit app

    st.set_page_config(layout="wide")

    st.markdown("<h1 style='text-align: center; color: black;'> Panel </h1>",
                unsafe_allow_html=True)
    st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    # --------- User input
    st.markdown("<h3 style='text-align: center; color: black;'>USER INPUT </h3>",
                unsafe_allow_html=True
    )




    def run(user_input):
        try:
            # specify Panel properties
            E = 73.0 * 10**9  # Pa
            nu = 0.33
            lambda_ = nu * E / ((1 + nu) * (1 - 2 * nu))  # Pa
            mu_real = E / (2 * (1 + nu))  # Pa
            lambda_ = lambda_ / mu_real  # Dimensionless
            mu = 1.0  # Dimensionless

            # make list of nodes to unroll graph on
            le = LinearElasticityPlaneStress(lambda_=lambda_, mu=mu)
            elasticity_net = instantiate_arch(
                input_keys=[Key("x"), Key("y"), Key("sigma_hoop")],
                output_keys=[
                    Key("u"),
                    Key("v"),
                    Key("sigma_xx"),
                    Key("sigma_yy"),
                    Key("sigma_xy"),
                ],
                cfg=cfg.arch.fully_connected,
            )
            nodes = le.make_nodes() + [elasticity_net.make_node(name="elasticity_network")]

            # add constraints to solver
            # make geometry
            x, y, sigma_hoop = Symbol("x"), Symbol("y"), Symbol("sigma_hoop")
            panel_origin = (-0.5, -0.9)
            panel_dim = (1, 1.8)  # Panel width is the characteristic length.
            window_origin = (-0.125, -0.2)
            window_dim = (0.25, 0.4)
            panel_aux1_origin = (-0.075, -0.2)
            panel_aux1_dim = (0.15, 0.4)
            panel_aux2_origin = (-0.125, -0.15)
            panel_aux2_dim = (0.25, 0.3)
            hr_zone_origin = (-0.2, -0.4)
            hr_zone_dim = (0.4, 0.8)
            circle_nw_center = (-0.075, 0.15)
            circle_ne_center = (0.075, 0.15)
            circle_se_center = (0.075, -0.15)
            circle_sw_center = (-0.075, -0.15)
            circle_radius = 0.05
            panel = Rectangle(
                panel_origin, (panel_origin[0] + panel_dim[0], panel_origin[1] + panel_dim[1])
            )
            window = Rectangle(
                window_origin,
                (window_origin[0] + window_dim[0], window_origin[1] + window_dim[1]),
            )
            panel_aux1 = Rectangle(
                panel_aux1_origin,
                (
                    panel_aux1_origin[0] + panel_aux1_dim[0],
                    panel_aux1_origin[1] + panel_aux1_dim[1],
                ),
            )
            panel_aux2 = Rectangle(
                panel_aux2_origin,
                (
                    panel_aux2_origin[0] + panel_aux2_dim[0],
                    panel_aux2_origin[1] + panel_aux2_dim[1],
                ),
            )
            hr_zone = Rectangle(
                hr_zone_origin,
                (hr_zone_origin[0] + hr_zone_dim[0], hr_zone_origin[1] + hr_zone_dim[1]),
            )
            circle_nw = Circle(circle_nw_center, circle_radius)
            circle_ne = Circle(circle_ne_center, circle_radius)
            circle_se = Circle(circle_se_center, circle_radius)
            circle_sw = Circle(circle_sw_center, circle_radius)
            corners = (
                window - panel_aux1 - panel_aux2 - circle_nw - circle_ne - circle_se - circle_sw
            )
            window = window - corners
            geo = panel - window
            hr_geo = geo & hr_zone

            # Parameterization
            characteristic_length = panel_dim[0]
            characteristic_disp = 0.001 * window_dim[0]
            sigma_normalization = characteristic_length / (mu_real * characteristic_disp)
            sigma_hoop_lower = 46 * 10**6 * sigma_normalization
            sigma_hoop_upper = 56.5 * 10**6 * sigma_normalization
            sigma_hoop_range = (sigma_hoop_lower, sigma_hoop_upper)
            param_ranges = {sigma_hoop: sigma_hoop_range}
#            inference_param_ranges = {sigma_hoop: 46 * 10**6 * sigma_normalization}
            inference_param_ranges = {sigma_hoop: user_input['val'] * 10**6 * sigma_normalization}
#             print('inference_param_ranges: ', inference_param_ranges)
            # bounds
            bounds_x = (panel_origin[0], panel_origin[0] + panel_dim[0])
            bounds_y = (panel_origin[1], panel_origin[1] + panel_dim[1])
            hr_bounds_x = (hr_zone_origin[0], hr_zone_origin[0] + hr_zone_dim[0])
            hr_bounds_y = (hr_zone_origin[1], hr_zone_origin[1] + hr_zone_dim[1])

            # make domain
            domain = Domain()

            # add inferencer data
            invar_numpy = geo.sample_interior(
                10,
                bounds={x: bounds_x, y: bounds_y},
                parameterization=inference_param_ranges,
            )
            point_cloud_inference = PointwiseInferencer(
                nodes=nodes,
                invar=invar_numpy,
                output_names=["u", "v", "sigma_xx", "sigma_yy", "sigma_xy"],
                batch_size=4096,
                plotter = InferencerPlotter()
            )
            domain.add_inferencer(point_cloud_inference, "inf_data")
            invar, outpred = point_cloud_inference.eval_epoch()
#             print(invar, outpred)
            input_sample = {'x': invar['x'], 'y': invar['y']}
#             print(input_sample)
            return point_cloud_inference.plotter(input_sample, outpred)
        except Exception as e:
            print(st.write(traceback.format_exc()))
            return []

        

    col1 = st.columns([1])

    val = col1[0].number_input(
        "Sigma",
        min_value=46.0,  # Adjust min_value to be a float
        max_value=56.5,
#         step=0.1,  # Adjust step to be compatible with floating-point numbers
        placeholder="Enter Sigma Value ...", 
        format="%.1f",
        key="sigma_input",  # Add a key for the input to ensure correct reactivity
    )


    submit = st.button("Predict", help="Click here to start prediction", 
                        type="primary", use_container_width=True,
    )
    st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    # ------- Prediction section 
    st.markdown(
        "<h1 style='text-align: center; color: black;'>PREDICTION </h1>",
        unsafe_allow_html=True
    )


    if submit == True: 
        # Create a dictionary with the user's input values  
        user_input = {  
            "val": val,
        }
        try:
            result = run(user_input)
            for x in result:
                img, name = x
                buffer = BytesIO()
                img.savefig(buffer, format='png')
                buffer.seek(0)
                image = Image.open(buffer)
                st.image(image)
        except Exception  as e:
            print(st.write(e), traceback.format_exc())
except Exception  as e:
    print(st.write(e), traceback.format_exc())


          
#     print(type(result), len(result))
