import { describe, it, expect } from 'vitest';
import {
  loginSchema,
  registerSchema,
  updateProfileSchema,
  changePasswordSchema,
} from './validation';

describe('validation schemas', () => {
  describe('loginSchema', () => {
    it('should validate correct login data', () => {
      const validData = {
        email: 'test@example.com',
        password: 'password',
      };
      
      const result = loginSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject invalid email', () => {
      const invalidData = {
        email: 'invalid-email',
        password: 'password',
      };
      
      const result = loginSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toBe('Invalid email address');
      }
    });

    it('should reject empty password', () => {
      const invalidData = {
        email: 'test@example.com',
        password: '',
      };
      
      const result = loginSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toBe('Password is required');
      }
    });
  });

  describe('registerSchema', () => {
    it('should validate correct registration data', () => {
      const validData = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'TestPass123!',
        confirmPassword: 'TestPass123!',
      };
      
      const result = registerSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject weak password', () => {
      const invalidData = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'weak',
        confirmPassword: 'weak',
      };
      
      const result = registerSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toContain('at least 8 characters');
      }
    });

    it('should reject password without uppercase', () => {
      const invalidData = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'testpass123!',
        confirmPassword: 'testpass123!',
      };
      
      const result = registerSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toContain('uppercase letter');
      }
    });

    it('should reject mismatched passwords', () => {
      const invalidData = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'TestPass123!',
        confirmPassword: 'DifferentPass123!',
      };
      
      const result = registerSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toBe("Passwords don't match");
      }
    });

    it('should reject short username', () => {
      const invalidData = {
        email: 'test@example.com',
        username: 'ab',
        password: 'TestPass123!',
        confirmPassword: 'TestPass123!',
      };
      
      const result = registerSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toContain('at least 3 characters');
      }
    });

    it('should reject username with invalid characters', () => {
      const invalidData = {
        email: 'test@example.com',
        username: 'test@user',
        password: 'TestPass123!',
        confirmPassword: 'TestPass123!',
      };
      
      const result = registerSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toContain('letters, numbers, underscores, and hyphens');
      }
    });
  });

  describe('updateProfileSchema', () => {
    it('should validate partial update', () => {
      const validData = {
        email: 'new@example.com',
      };
      
      const result = updateProfileSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should validate empty update', () => {
      const validData = {};
      
      const result = updateProfileSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject invalid email in update', () => {
      const invalidData = {
        email: 'invalid-email',
      };
      
      const result = updateProfileSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });
  });

  describe('changePasswordSchema', () => {
    it('should validate correct password change data', () => {
      const validData = {
        currentPassword: 'OldPass123!',
        newPassword: 'NewPass123!',
        confirmPassword: 'NewPass123!',
      };
      
      const result = changePasswordSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject when new passwords do not match', () => {
      const invalidData = {
        currentPassword: 'OldPass123!',
        newPassword: 'NewPass123!',
        confirmPassword: 'DifferentPass123!',
      };
      
      const result = changePasswordSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toBe("Passwords don't match");
      }
    });

    it('should reject weak new password', () => {
      const invalidData = {
        currentPassword: 'OldPass123!',
        newPassword: 'weak',
        confirmPassword: 'weak',
      };
      
      const result = changePasswordSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toContain('at least 8 characters');
      }
    });
  });
});