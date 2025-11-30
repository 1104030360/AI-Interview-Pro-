import React, { useState } from 'react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { apiClient } from '../services/api';

interface LoginProps {
    onLoginSuccess: () => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // 使用 apiClient.login 確保 token 正確保存
            await apiClient.login({ email, password });
            onLoginSuccess();
        } catch (err: any) {
            setError(err.message || 'Login failed. Please check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    const fillDevCredentials = () => {
        setEmail('dev@test.com');
        setPassword('dev123456');
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-surface to-background flex items-center justify-center p-6">
            <Card className="w-full max-w-md p-8">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent mb-2">
                        AI Interview Pro
                    </h1>
                    <p className="text-textSecondary">Sign in to continue</p>
                </div>

                <form onSubmit={handleLogin} className="space-y-6">
                    <div>
                        <label htmlFor="email" className="block text-sm font-medium text-textMain mb-2">
                            Email
                        </label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-4 py-3 rounded-lg bg-surface border border-surface-hover text-textMain placeholder-textSecondary focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                            placeholder="Enter your email"
                            required
                        />
                    </div>

                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-textMain mb-2">
                            Password
                        </label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-4 py-3 rounded-lg bg-surface border border-surface-hover text-textMain placeholder-textSecondary focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                            placeholder="Enter your password"
                            required
                        />
                    </div>

                    {error && (
                        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    <Button
                        type="submit"
                        disabled={loading}
                        className="w-full"
                    >
                        {loading ? 'Signing in...' : 'Sign In'}
                    </Button>

                    <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-surface-hover"></div>
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-surface px-2 text-textSecondary">Development Mode</span>
                        </div>
                    </div>

                    <Button
                        type="button"
                        onClick={fillDevCredentials}
                        variant="secondary"
                        className="w-full"
                    >
                        Fill Dev Credentials
                    </Button>

                    <div className="text-center text-xs text-textSecondary">
                        <p>Dev Account:</p>
                        <p className="font-mono mt-1">dev@test.com / dev123456</p>
                    </div>
                </form>
            </Card>
        </div>
    );
};
