# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 18:41:30 2014

@author: Open Risk
"""


from scipy import stats
from sympy import binomial
import math


def vasicek_base(N, k, p, rho):
    zmin = -7
    zmax = 7    
    grid = 2000
    dz = float(zmax - zmin) / float(grid - 1)
    a = stats.norm.ppf(p, loc=0.0, scale=1.0)
    integral = 0
    for i in range(1, grid):
        z = zmin + dz * i
        arg = (a - rho * z) / math.sqrt(1 - rho * rho)
        phi_den = stats.norm.pdf(z, loc=0.0, scale=1.0)
        phi_cum = stats.norm.cdf(arg, loc=0.0, scale=1.0)
        integrant = phi_den * math.pow(phi_cum,k) * math.pow(1 - phi_cum,N - k) * binomial(N, k)
        integral = integral + integrant
    return dz * integral


def vasicek_base_el(N, p, rho):
    return N * p  


def vasicek_base_ul(N, p, rho):
    zmin = -7
    zmax = 7    
    grid = 2000
    dz = float(zmax - zmin) / float(grid - 1)
    a = stats.norm.ppf(p, loc=0.0, scale=1.0)
    integral = 0
    for i in range(1, grid):
        z = zmin + dz * i
        arg = (a - rho * z) / math.sqrt(1 - rho * rho)
        phi_den = stats.norm.pdf(z, loc=0.0, scale=1.0)
        phi_cum = stats.norm.cdf(arg, loc=0.0, scale=1.0)
        integrant = phi_den * math.pow(phi_cum,2)
        integral = integral + integrant
    result = p/N - p*p + float(N-1)/float(N) * dz * integral
    return N * math.sqrt(result)    


def vasicek_lim(theta, p, rho):
    a1 = stats.norm.ppf(p, loc=0.0, scale=1.0)
    arg1 = stats.norm.ppf(theta, loc=0.0, scale=1.0)
    arg2 = ( math.sqrt(1-rho*rho) * arg1 - a1) / rho
    result = stats.norm.cdf(arg2, loc=0.0, scale=1.0)   
    return result


def vasicek_lim_el(p, rho):
    return p      


def vasicek_lim_ul(p, rho):
    zmin = -7
    zmax = 7    
    grid = 4000
    dz = float(zmax - zmin) / float(grid - 1)
    a = stats.norm.ppf(p, loc=0.0, scale=1.0)
    integral = 0
    for i in range(1, grid):
        z = zmin + dz * i
        arg = (a - rho * z) / math.sqrt(1 - rho * rho)
        phi_den = stats.norm.pdf(z, loc=0.0, scale=1.0)
        phi_cum = stats.norm.cdf(arg, loc=0.0, scale=1.0)
        integrant = phi_den * math.pow(phi_cum,2)
        integral = integral + integrant
    result = - p*p + dz * integral
    return math.sqrt(result)      


def vasicek_lim_q(alpha, p, rho):
    a1 = stats.norm.ppf(p, loc=0.0, scale=1.0)
    a2 = stats.norm.ppf(alpha, loc=0.0, scale=1.0)
    arg = (a1 + rho * a2) / math.sqrt(1 - rho * rho)
    return stats.norm.cdf(arg, loc=0.0, scale=1.0)  