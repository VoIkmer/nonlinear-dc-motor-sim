import numpy as np
import control as ct


def default_params():
    return {
        'Ra': 2.0,
        'La': 0.5,
        'Km': 0.1,
        'J': 0.02,
        'Bm': 0.01,
        'k': 0.001,
        'Va0': 24.0,
    }


def operating_point(params):
    # Solve a*w0^2 + b*w0 + c = 0 for positive root
    a = params['k']
    b = params['Bm'] + (params['Km']**2) / params['Ra']
    c = - (params['Km'] * params['Va0']) / params['Ra']
    roots = np.roots([a, b, c])
    w0_candidates = [r for r in roots if np.isreal(r) and r > 0]
    if not w0_candidates:
        w0 = np.real(roots[0])
    else:
        w0 = np.real(w0_candidates[0])
    ia0 = (params['Va0'] - params['Km']*w0) / params['Ra']
    return w0, ia0


def linearize_system(params, w0):
    Beq = params['Bm'] + 2 * params['k'] * w0
    A = np.array([
        [-params['Ra']/params['La'], -params['Km']/params['La']],
        [params['Km']/params['J'],   -Beq/params['J']]
    ])
    B = np.array([[1/params['La']], [0]])
    C = np.array([[0, 1]])
    D = np.array([[0]])
    ss = ct.ss(A, B, C, D)
    return ss, Beq


def to_transfer(ss):
    return ct.ss2tf(ss)


def dc_gain(sys):
    return ct.dcgain(sys)


def step_response(sys, T=None):
    return ct.step_response(sys, T=T)


def forced_response(sys, T, U):
    return ct.forced_response(sys, T=T, U=U)


def design_pid_by_pole_placement(G_s, desired_poles):
    # Solve Diophantine for PID gains given desired polynomial
    # desired_poles: list of complex roots
    poly = np.poly(desired_poles)
    alpha2 = poly[1]
    alpha1 = poly[2]
    alpha0 = poly[3]
    num = G_s.num[0][0]
    den = G_s.den[0][0]
    c0 = num[-1]
    a1 = den[1]
    a2 = den[2]
    Kd = (alpha2 - a1) / c0
    Kp = (alpha1 - a2) / c0
    Ki = alpha0 / c0
    return float(Kp), float(Ki), float(Kd)
