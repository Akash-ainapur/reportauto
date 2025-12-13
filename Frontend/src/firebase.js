import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyCVwo036lVroxLK0GJlN6jHhhD6Ji0CGHw",
  authDomain: "report-auto-972c2.firebaseapp.com",
  projectId: "report-auto-972c2",
  storageBucket: "report-auto-972c2.firebasestorage.app",
  messagingSenderId: "50638043012",
  appId: "1:50638043012:web:81eab1d3e92e04d6614fd1",
  measurementId: "G-81YQ0RD8YD"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
