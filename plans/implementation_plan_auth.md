# Implementing Clerk Authentication & Freemium Logic

## Goal
Replace the "Waitlist" on the landing page with direct Clerk Authentication (Login/Signup). Users should be able to log in and be redirected to the Report Generation dashboard.

## Proposed Changes

### Frontend
#### [MODIFY] `Frontend/src/pages/LandingPage.jsx`
- **Imports**: Add `SignedIn`, `SignedOut`, `SignInButton` from `@clerk/clerk-react`.
- **UI Changes**:
  - Remove `<Waitlist />`.
  - **SignedOut State**: Show "Get Started" button. Clicking it opens the Clerk Modal (`<SignInButton mode="modal">`).
  - **SignedIn State**: Show "Go to Dashboard" button. Clicking it links to `/generate`.
- **Styling**: Reuse the existing gradient/glassmorphism styles for the buttons.

### Verification Plan
1.  **Landing Page**: Open `/`. Expect "Get Started" button. Click it -> Login Modal.
2.  **Auth Flow**: Sign in. Expect button to change to "Go to Dashboard".
3.  **Redirect**: Click "Go to Dashboard". Verify arrival at `/generate`.
