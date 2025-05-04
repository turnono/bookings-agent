# Firestore Collection Structure Migration Plan

This document outlines the plan for a potential future migration from our current nested collection structure (`users/{userId}/bookings/{bookingId}`) to a flat collection structure (`bookings/{bookingId}`) if analytics and administrative dashboards become a priority.

## Current Structure

- **Nested Collections**: `users/{userId}/bookings/{bookingId}`
- **Benefits**: Natural user data isolation, intuitive security model, efficient user-specific queries
- **Limitations**: Requires collection group queries for cross-user analytics, slightly more complex admin dashboard implementation

## Target Structure

- **Flat Collections**: `bookings/{bookingId}` with `userId` field
- **Benefits**: Simpler analytics queries, more straightforward admin dashboards, resilience to anonymous UID changes
- **Limitations**: Requires explicit filtering for user-specific data, more complex security rules

## Migration Process

### 1. Preparation Phase

1. **Create Collections and Indexes**

   - Create the `bookings` top-level collection
   - Set up necessary indexes for the `userId` field
   - Add any additional fields needed for analytics

2. **Update Security Rules**

   - Implement security rules for the flat structure
   - Test security with the Firebase emulator

3. **Develop Migration Script**
   - Create a Cloud Function for data migration
   - Include validation and error handling
   - Test with a small subset of data

### 2. Migration Execution

1. **Data Duplication (No Downtime)**

   - First duplicate existing data from `users/{userId}/bookings/{bookingId}` to `bookings/{bookingId}`
   - Keep both structures in sync temporarily via triggers
   - Validate data consistency between both structures

2. **Code Update**

   - Deploy updated FirestoreService implementation that uses the flat structure
   - Implement feature flags to enable gradual rollout
   - Add backward compatibility for existing sessions

3. **Validation and Monitoring**
   - Monitor for any issues or edge cases
   - Validate analytics queries work correctly
   - Check security rules effectiveness

### 3. Cleanup Phase

1. **Deprecate Old Structure**

   - Once confident in the new structure, stop writing to the old structure
   - Maintain read capabilities for historical data
   - Update documentation and code comments

2. **Data Archival**
   - Archive the old structure after a suitable period
   - Can be read-only for historical reference
   - Consider data export for long-term storage if needed

## Implementation Considerations

### Code Changes

```typescript
// Before: Nested structure
const bookingsCollection = this.client
  .collection("users")
  .document(userId)
  .collection("bookings");

// After: Flat structure
const bookingsCollection = this.client.collection("bookings");
// For user-specific queries
const userBookings = bookingsCollection.where("userId", "==", userId);
```

### Security Rules Updates

```
// Before: Nested structure
match /users/{userId}/bookings/{bookingId} {
  allow read, write: if request.auth != null && request.auth.uid == userId;
}

// After: Flat structure
match /bookings/{bookingId} {
  allow read: if request.auth != null && request.auth.uid == resource.data.userId;
  allow write: if request.auth != null && request.auth.uid == request.resource.data.userId;
}
```

### Analytics Queries

```typescript
// Before: Collection group query
const allBookings = firebase.firestore().collectionGroup("bookings");

// After: Direct collection query
const allBookings = firebase.firestore().collection("bookings");
```

## Rollback Plan

In case of issues during migration:

1. Revert code changes to use the original nested structure
2. Keep the duplicated data for reference
3. Analyze issues and refine the migration approach

## Timeline Estimation

- Preparation: 1-2 weeks
- Migration: 1-2 days (depending on data volume)
- Validation: 1 week
- Cleanup: After 2-4 weeks of successful operation
