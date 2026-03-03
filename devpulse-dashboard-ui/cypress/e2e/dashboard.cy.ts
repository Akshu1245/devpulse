/// <reference types="cypress" />

describe('DevPulse Dashboard', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('loads the dashboard page with v4.0 branding', () => {
    cy.contains('DevPulse').should('be.visible');
    cy.contains('v4.0').should('be.visible');
    cy.contains('LIVE').should('be.visible');
  });

  it('displays overview section', () => {
    cy.contains('Overview').should('be.visible');
  });

  it('shows Pillar 1 — AI API Security Scanner', () => {
    cy.contains('Pillar 1').should('exist');
    cy.contains('AI API Security Scanner').should('exist');
  });

  it('shows Pillar 2 — API Cost Intelligence', () => {
    cy.contains('Pillar 2').should('exist');
    cy.contains('API Cost Intelligence').should('exist');
  });

  it('shows Core Tools section', () => {
    cy.contains('Core Tools').should('exist');
  });

  it('shows health monitor', () => {
    cy.contains('Health Monitor').should('exist');
  });

  it('shows billing panel', () => {
    cy.contains('Billing').should('exist');
  });

  it('footer shows v4.0 branding', () => {
    cy.scrollTo('bottom');
    cy.contains('All systems operational').should('be.visible');
    cy.contains('AI API Security').should('exist');
  });
});
