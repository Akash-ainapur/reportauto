import { SignIn } from "@clerk/clerk-react";
import Navbar from "../components/Navbar";

const AuthPage = () => {
    return (
        <div className="min-h-screen pt-24 pb-12 px-4 bg-background flex flex-col items-center justify-center">
            <Navbar />
            <div className="w-full max-w-md">
                <SignIn />
            </div>
        </div>
    );
};

export default AuthPage;
