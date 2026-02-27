import numpy as np
import matplotlib.pyplot as plt


# --- placeholders for your MATLAB functions ---
def systempra():
    """Return a dict-like system parameter set.
    Replace with your real implementation.
    Required keys: r, z, re, wl
    """
    return {
        "r": 1.0,
        "z": 1.0,
        "re": 256,
        "wl": 0.5,
    }


def IPSF_Vectorial_Linear_xy(sys, X, Y):
    """Replace with your real implementation.
    Should return Ix, Iy, Iz, I as 2D arrays shaped (len(Y), len(X)).
    """
    XX, YY = np.meshgrid(X, Y, indexing="xy")
    I = np.exp(-(XX**2 + YY**2))
    Ix = I * 0.5
    Iy = I * 0.5
    Iz = np.zeros_like(I)
    return Ix, Iy, Iz, I


def IPSF_Vectorial_Linear_rz(sys, R, Z, ang):
    """Replace with your real implementation.
    Should return Ex, Ey, Ez, Ix, Iy, Iz, I as 2D arrays shaped (len(Z), len(R)).
    """
    RR, ZZ = np.meshgrid(R, Z, indexing="xy")
    I = np.exp(-(RR**2 + ZZ**2))
    Ex = RR * 0.0 + 1.0
    Ey = ZZ * 0.0
    Ez = np.zeros_like(I)
    Ix = I * 0.5
    Iy = I * 0.5
    Iz = np.zeros_like(I)
    return Ex, Ey, Ez, Ix, Iy, Iz, I


def ExtractColormap(n=1024):
    """MATLAB custom colormap replacement."""
    return plt.get_cmap("jet", n)


def main():
    sys = systempra()

    X = np.linspace(-sys["r"], sys["r"], sys["re"])
    Y = np.linspace(-sys["r"], sys["r"], sys["re"])
    R = np.linspace(-sys["r"], sys["r"], sys["re"])
    Z = np.linspace(-sys["z"], sys["z"], sys["re"])

    ang = 0
    re2 = 210
    R2 = np.linspace(-sys["r"], sys["r"], re2)
    Z2 = np.linspace(-sys["z"], sys["z"], re2)

    # [Ix, Iy, Iz, I] = IPSF_Vectorial_Linear_xy(sys, X, Y);
    Ix, Iy, Iz, I = IPSF_Vectorial_Linear_xy(sys, X, Y)

    # figure(1)
    plt.figure(1)
    plt.imshow(
        I,
        extent=[X[0] / sys["wl"], X[-1] / sys["wl"], Y[0] / sys["wl"], Y[-1] / sys["wl"]],
        origin="lower",
        aspect="auto",
        cmap=ExtractColormap(1024),
    )
    plt.colorbar()
    plt.xlabel("x(/lambda)")
    plt.ylabel("y(/lambda)")

    x, y = np.meshgrid(X, Y, indexing="xy")
    r, z = np.meshgrid(R, Z, indexing="xy")

    # [Ex2, Ey2, ~, Ix2, Iy2, Iz2, I2] = IPSF_Vectorial_Linear_rz(sys, R2, Z2,ang);
    Ex2, Ey2, _, Ix2, Iy2, Iz2, I2 = IPSF_Vectorial_Linear_rz(sys, R2, Z2, ang)

    # Ez2 = zeros(length(R2),length(Z2)); % create Ez component for azimuthal only
    # MATLAB shape here is (len(R2), len(Z2)); for plotting/vector ops we use (len(Z2), len(R2))
    Ez2 = np.zeros((len(Z2), len(R2)))
    Er2 = Ex2.copy()

    r2, z2 = np.meshgrid(R2, Z2, indexing="xy")
    Er2[r2 < 0] = -Er2[r2 < 0]

    # figure(2)
    plt.figure(2)
    plt.imshow(
        I2,
        extent=[R[0] / sys["wl"], R[-1] / sys["wl"], Z[0] / sys["wl"], Z[-1] / sys["wl"]],
        origin="lower",
        aspect="auto",
        cmap=ExtractColormap(1024),
    )
    plt.colorbar()
    plt.xlabel("x(/lambda)")
    plt.ylabel("z(/lambda)")

    # Optional quiver overlay like MATLAB comments:
    # plt.quiver(r2, z2, Er2, Ez2, color='w', scale=50)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
