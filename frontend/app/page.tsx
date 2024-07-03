// Home.tsx
'use client'

import React from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import ExamSelector from './components/ExamSelector';

export default function Home() {

  return (
    <div className="main-container">
      <Header />
      <main className="content">
        <ExamSelector/>
      </main>
      <Footer />
    </div>
  );
}