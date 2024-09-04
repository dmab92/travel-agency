/** @odoo-module */
import {register } from "@web/core/registry"

const {Component } =owl

export class OwlSalesDashboard extends Component{}

OwlSalesDashboard.template ="owl.OwlSalesDashboard"

registry.category('actions').add("owl.sales_dashboard",OwlSalesDashboard)